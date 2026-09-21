# langchain 1.1以后支持 模型 profile

import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from rich import print as rprint

from utils import stream_response

load_dotenv(override=True)

llm_deepseek = init_chat_model(
    api_base=os.getenv("DEEPSEEK_API_BASE"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-flash",
    model_provider="deepseek",
)

print(llm_deepseek.profile)

# 模型初始化完整参数
rprint(ChatDeepSeek.model_fields.items())
