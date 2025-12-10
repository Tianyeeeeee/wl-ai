import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
        if base_url.endswith("/chat/completions"):
            base_url = base_url.replace("/chat/completions", "")

        self.client = AsyncOpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=base_url
        )
        self.model_name = os.getenv("LLM_MODEL_NAME", "deepseek-chat")

    async def chat_completion(self, messages, tools=None, tool_choice="auto", temperature=0.1, stream=False):
        """
        🔥 唯一修改：增加 stream=False 参数，并透传给 SDK
        """
        params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "stream": stream, # 开启流式
            "timeout": 60.0
        }

        if tools and len(tools) > 0:
            params["tools"] = tools
            params["tool_choice"] = tool_choice

        # 直接返回 SDK 的响应对象（可能是 Response 或者是 Stream）
        return await self.client.chat.completions.create(**params)