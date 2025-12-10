import json
from typing import AsyncGenerator, List
from .llm import LLMService
from .tools import ToolManager
from .vector_store import VectorStore
from .sandbox import PythonSandbox
from .db_guard import SQLGuard
from .prompt import PromptBuilder

class AgentEngine:
    def __init__(self):
        print("🚀 [Agent] 初始化：Keep Logic & Enable Streaming...")
        self.llm = LLMService()
        self.tools = ToolManager()
        self.vector_store = VectorStore()
        self.sandbox = PythonSandbox()

    # --- 保持你的逻辑不变 ---
    def _extract_previous_data(self, history: List[dict]):
        for msg in reversed(history):
            if msg.get("role") == "tool":
                try:
                    content = json.loads(msg.get("content", "{}"))
                    if content.get("status") == "success" and content.get("data"):
                        return content["data"]
                except: continue
        return None

    # --- 保持你的逻辑不变 ---
    async def _execute_sql_with_retry(self, query: str):
        try:
            clean_sql = SQLGuard.validate(query)
        except ValueError as e:
            return {"status": "error", "message": str(e)}

        res = self.tools.execute("execute_sql", {"query": clean_sql})
        if res['status'] == 'success': return res

        # 失败重试逻辑 (内部调用不用流式，保持 stream=False)
        error_msg = res['message']
        print(f"⚠️ [SQL Fail] {error_msg} -> Auto-fixing...")
        
        fix_prompt = f"SQL: {clean_sql}\nError: {error_msg}\nFix the SQL syntax. Output ONLY SQL."
        try:
            resp = await self.llm.chat_completion([
                {"role": "system", "content": "Output ONLY SQL. No markdown."},
                {"role": "user", "content": fix_prompt}
            ], temperature=0.0, stream=False) # 内部修复不流式
            
            fixed_sql = resp.choices[0].message.content.strip().replace("```sql", "").replace("```", "")
            clean_sql = SQLGuard.validate(fixed_sql)
            return self.tools.execute("execute_sql", {"query": clean_sql})
        except Exception as e:
            return {"status": "error", "message": f"Auto-fix failed: {e}"}

    async def run(self, history: List[dict]) -> AsyncGenerator[dict, None]:
        last_msg = history[-1]['content']
        intent = "DATA" if any(k in last_msg for k in ["查", "分析", "图", "数", "多少", "select", "排名"]) else "CHAT"

        # ----------------------------------------------------
        # 场景 1：闲聊模式 (增加流式)
        # ----------------------------------------------------
        if intent == "CHAT":
            yield {"type": "trace", "data": {"status": "info", "message": "闲聊模式"}}
            
            # 🔥 开启流式
            stream = await self.llm.chat_completion(history, temperature=0.7, stream=True)
            
            full_content = ""
            async for chunk in stream:
                if chunk.choices:
                    token = chunk.choices[0].delta.content
                    if token:
                        full_content += token
                        # 🔥 实时吐字
                        yield {"type": "text", "content": token}
            return

        # ----------------------------------------------------
        # 场景 2：数据模式 (RAG + 工具 + 流式)
        # ----------------------------------------------------
        prev_data = self._extract_previous_data(history)
        context_data_buffer = prev_data if prev_data else []
        tools = self.tools.get_definitions()
        
        if context_data_buffer and any(k in last_msg for k in ["分析", "画", "图", "解释"]):
            print("🧠 [Mode] Analysis")
            prompt = PromptBuilder.build_analysis_prompt(json.dumps(context_data_buffer[:3], ensure_ascii=False), len(context_data_buffer))
            tools = [t for t in tools if t['function']['name'] != 'execute_sql']
        else:
            print("🧠 [Mode] RAG Query")
            rag_results = self.vector_store.retrieve(last_msg, top_k=8)
            prompt = PromptBuilder.build_system_prompt(rag_results)

        msgs = [{"role": "system", "content": prompt}] + history[-5:]

        # 3轮交互 Loop
        for i in range(3):
            yield {"type": "trace", "data": {"status": "thinking", "message": "思考中..."}}
            
            # 🔥 开启流式
            stream = await self.llm.chat_completion(msgs, tools=tools, temperature=0.0, stream=True)
            
            full_content = ""
            tool_calls_buffer = []
            current_tool_index = -1
            
            # 🔥 逐块接收并处理
            async for chunk in stream:
                if not chunk.choices: continue
                delta = chunk.choices[0].delta

                # A. 文本内容 -> 实时发给前端 (Thought)
                if delta.content:
                    token = delta.content
                    full_content += token
                    yield {"type": "thought", "content": token}

                # B. 工具调用 -> 必须拼接碎片 (不能直接发)
                if delta.tool_calls:
                    for tool_delta in delta.tool_calls:
                        index = tool_delta.index
                        
                        # 新工具开始
                        if index > current_tool_index:
                            tool_calls_buffer.append({
                                "id": tool_delta.id,
                                "type": "function",
                                "function": {
                                    "name": tool_delta.function.name,
                                    "arguments": ""
                                }
                            })
                            current_tool_index = index
                        
                        # 拼接参数
                        if tool_delta.function.arguments:
                            tool_calls_buffer[index]["function"]["arguments"] += tool_delta.function.arguments

            # --- 流式接收完毕，开始执行逻辑 (和原来一样) ---
            
            if not tool_calls_buffer:
                if full_content:
                    yield {"type": "text", "content": full_content}
                break

            # 存入历史
            msgs.append({
                "role": "assistant",
                "content": full_content,
                "tool_calls": tool_calls_buffer
            })

            for tool_call in tool_calls_buffer:
                func_name = tool_call["function"]["name"]
                args = self.tools.parse_args(tool_call["function"]["arguments"])
                
                yield {"type": "trace", "data": {"status": "executing", "tool": func_name}}
                
                tool_result = {}

                # 1. SQL
                if func_name == "execute_sql":
                    res = await self._execute_sql_with_retry(args.get("query"))
                    if res['status'] == 'success':
                        data = res['data']
                        context_data_buffer = data
                        summary = f"Query returned {len(data)} rows."
                        yield {"type": "table", "data": data[:50], "summary": summary}
                        tool_result = {"status": "success", "message": summary, "data": data}
                    else:
                        tool_result = {"status": "error", "message": res['message']}
                
                # 2. Chart (不执行，直接返回前端)
                elif func_name == "generate_chart":
                    if not context_data_buffer:
                        tool_result = {"status": "error", "message": "No data available."}
                    else:
                        yield {
                            "type": "chart",
                            "data": context_data_buffer,
                            "config": {
                                "type": args.get("chart_type", "bar"),
                                "xKey": args.get("x_key"),
                                "yKey": args.get("y_key"),
                                "title": args.get("title", "Chart")
                            }
                        }
                        tool_result = {"status": "success", "message": "Chart sent to frontend."}

                # 3. Python
                elif func_name == "execute_python":
                    if not context_data_buffer:
                        tool_result = {"status": "error", "message": "No data found."}
                    else:
                        py_res = self.sandbox.execute(args.get("code"), data_context=context_data_buffer)
                        if py_res['success']:
                            tool_result = {"status": "success", "output": py_res['stdout']}
                            yield {"type": "text", "content": f"```\n{py_res['stdout']}\n```"}
                            if py_res.get('chart_config'):
                                 yield {"type": "chart", "config": py_res['chart_config']}
                        else:
                            tool_result = {"status": "error", "message": py_res['error']}

                msgs.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })