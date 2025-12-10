from openai import OpenAI
import os

# 1. 配置你的参数
API_KEY = "sk-tDCjIrUKeOC4oIot69G4Uf5ubP0TLUACqLcsXYG74PI3HGvs" # 你的 Key
BASE_URL = "https://aimodels.leapmotor.com/v1" # 注意：这里不要写 /chat/completions
MODEL_NAME = "deepseek-v3.1"

print(f"🔄 正在测试连接: {BASE_URL} ...")

try:
    # 2. 初始化客户端
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    # 3. 发起流式请求
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": "你好，DeepSeek，请回复'测试成功'四个字。"}],
        stream=True,
        stream_options={"include_usage": True} # 你要求的参数
    )

    print("✅ 连接成功！接收流式数据中：")
    print("-" * 30)

    # 4. 打印结果
    full_content = ""
    for chunk in response:
        # 处理 usage 信息 (通常在最后一个包)
        if hasattr(chunk, 'usage') and chunk.usage:
            print(f"\n[Usage Info] Prompt: {chunk.usage.prompt_tokens}, Total: {chunk.usage.total_tokens}")
            continue

        if chunk.choices and len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="", flush=True)
                full_content += delta.content

    print("\n" + "-" * 30)
    print("测试结束。")

except Exception as e:
    print(f"\n❌ 连接失败！错误详情:\n{e}")
    print("\n请检查：\n1. API Key 是否正确\n2. pip install --upgrade openai (需要最新版才支持 stream_options)")