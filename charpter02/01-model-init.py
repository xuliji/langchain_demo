import os

from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv

load_dotenv(override=True)

llm_deepseek = ChatDeepSeek(
    # api_base=os.getenv("DEEPSEEK_API_BASE"),
    # api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-flash")

response = llm_deepseek.invoke("uv.lock是什么文件？有什么作用")
print(response.content)
