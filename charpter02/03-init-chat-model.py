import os

from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv(override=True)

llm_deepseek = init_chat_model(
    api_base=os.getenv("DEEPSEEK_API_BASE"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-flash",
    model_provider="deepseek",
)

response = llm_deepseek.invoke("uv.lock是什么文件？有什么作用")
print(response.content)
