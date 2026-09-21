import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from utils import stream_response

load_dotenv(override=True)

llm_deepseek = init_chat_model(
    api_base=os.getenv("DEEPSEEK_API_BASE"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-flash",
    model_provider="deepseek",
)


messages = [
    SystemMessage(content="你是一个有帮助的 AI 助手。请用卢本伟的语气和我说话。")
]
while True:
    user_content = input("请输入问题：")
    if user_content == "/quit":
        break
    messages.append(HumanMessage(content=user_content))
    response = stream_response(llm_deepseek.stream(messages))
    messages.append(AIMessage(content=response.content))
