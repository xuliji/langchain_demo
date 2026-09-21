import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(override=True)

chat = ChatOpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),
                  base_url=os.getenv("DEEPSEEK_BASE_URL"),
                  model="deepseek-flash")

invoke = chat.invoke("1+1等于几")
print(invoke)
