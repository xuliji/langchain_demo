import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from rich import print as rprint

from charpter02 import utils

load_dotenv(override=True)

model = init_chat_model(
    api_base=os.getenv("DEEPSEEK_API_BASE"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-flash",
    model_provider="deepseek",
)

messages = [
    SystemMessage(content="你是杀生鱼丸 请用杀生鱼丸的口吻和我对话 要俏皮一点的")
]

while True:
    user_input = input("请输入问题：")
    if user_input == "exit":
        break
    messages.append(HumanMessage(content=user_input))
    ai_message = utils.stream_response(model.stream(messages))
    messages.append(ai_message)
