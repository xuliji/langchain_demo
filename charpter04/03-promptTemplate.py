
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate

chat_prompt_template = ChatPromptTemplate.from_messages(
    [("system", "你是一个AI助手，你的名字叫{name}"),
     ("user", "你最近怎么样？"),
     ("ai", "我最近很好，我最近生了两个孩子,是一对双胞胎"),
     ("user", "{user_input}")]
)

prompt_value = chat_prompt_template.format_messages(name="小许", user_input="2+2=?")
print(prompt_value)

import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from rich import print as rprint

load_dotenv(override=True)

model = init_chat_model(
    api_base=os.getenv("DEEPSEEK_API_BASE"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-flash",
    model_provider="deepseek",
)

response = model.invoke(prompt_value)
rprint(response.content_blocks)
