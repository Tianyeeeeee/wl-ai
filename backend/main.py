# main.py
import uvicorn
import asyncio
import json
from contextlib import asynccontextmanager
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent import AgentEngine
from app.training import router as training_router
from app.training import auto_train


# 🔥 Vanna 模式的核心：服务启动后，后台静默建立索引
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 启动服务
    print("🚀 [System] 服务已启动 (Vanna-Like Mode)")

    # 2. 创建后台任务扫描数据库 (不阻塞主线程)
    asyncio.create_task(background_indexing_task())

    yield
    print("👋 [System] 服务关闭")


async def background_indexing_task():
    """后台全量扫描数据库，建立 RAG 索引"""
    print("⏳ [Background] 开始全量扫描数据库 Schema (构建知识库)...")
    loop = asyncio.get_event_loop()
    try:
        # 在线程池运行，防止卡顿
        result = await loop.run_in_executor(None, auto_train)
        print(f"✅ [Background] 知识库构建完成: {result['message']}")
    except Exception as e:
        print(f"❌ [Background] 扫描失败 (请检查数据库连接): {e}")


app = FastAPI(lifespan=lifespan)

# 注册训练接口 (你可以手动调用 API 来补充文档或 SQL 对)
app.include_router(training_router)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

engine = AgentEngine()


class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]


async def sse_stream(history: List[Dict[str, Any]]):
    yield "data: {\"type\": \"ping\", \"content\": \"connected\"}\n\n"
    try:
        async for event in engine.run(history):
            payload = json.dumps(event, ensure_ascii=False)
            yield f"data: {payload}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        print(f"❌ Error: {e}")
        err = json.dumps({"type": "error", "content": str(e)}, ensure_ascii=False)
        yield f"data: {err}\n\n"


@app.post("/api/rag/chat")
async def api_chat(req: ChatRequest):
    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(sse_stream(req.messages), headers=headers, media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=927)