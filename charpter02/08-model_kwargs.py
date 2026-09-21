import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, ToolMessage

from utils import get_weather

load_dotenv(override=True)


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的实时天气，包括温度、湿度和风速。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海、深圳。",
                    }
                },
                "required": ["city"],
            },
        },
    }
]

model = init_chat_model(
    api_base=os.getenv("DEEPSEEK_API_BASE"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-flash",
    model_provider="deepseek",
    model_kwargs={
        "tools": tools,
        "tool_choice": "auto",
    },
)

tool_map = {
    "get_weather": get_weather,
}

messages = [
    HumanMessage(content="帮我查询一下北京现在的天气，并用一句话总结。")
]

# 第一次请求：让模型判断是否需要调用工具。
response = model.invoke(messages)
messages.append(response)

if response.tool_calls:
    for tool_call in response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        print(f"模型请求调用工具：{tool_name}")
        print(f"工具参数：{tool_args}")

        tool_result = tool_map[tool_name](**tool_args)
        print(f"工具返回：{tool_result}")

        messages.append(
            ToolMessage(
                content=tool_result,
                tool_call_id=tool_call["id"],
            )
        )

    # 第二次请求：把工具结果交回模型，让模型生成自然语言回答。
    final_response = model.invoke(messages)
    print("AI 回复：", final_response.content)
else:
    print("AI 回复：", response.content)
