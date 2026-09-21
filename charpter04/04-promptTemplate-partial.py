## 预填充
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

chat_prompt_template = ChatPromptTemplate.from_messages(
    [("system", "你是一个AI助手，你的名字叫{name}"),
     ("user", "你最近怎么样？"),
     ("ai", "我最近很好，我最近生了两个孩子,是一对双胞胎"),
     ("user", "{user_input}")]
)

partial = chat_prompt_template.partial(name='小许')

prompt_value = partial.invoke({"user_input": "你生了几个孩子？"})

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

## placeholder
chat_prompt_template = ChatPromptTemplate.from_messages(
    [("system", "你是一个AI助手,请用沙身鱼丸的口吻和我对话要求要俏皮一点"),
     ("placeholder", "{conversation}")
     ]
)

prompt_template_invoke = chat_prompt_template.invoke({"conversation": [HumanMessage("今天天气怎么样啊？"),
                                                       AIMessage("今天天气晴朗，温度30度"),
                                                       HumanMessage("明天天气怎么样呢？")]})
rprint(prompt_template_invoke)


## MessagesPlaceholder
chat_prompt_template = ChatPromptTemplate.from_messages(
    [("system", "你是一个AI助手,请用沙身鱼丸的口吻和我对话要求要俏皮一点"),
     MessagesPlaceholder(variable_name="conversation")
     ]
)

prompt_template_invoke = chat_prompt_template.invoke({"conversation": [HumanMessage("今天天气怎么样啊？"),
                                                       AIMessage("今天天气晴朗，温度30度"),
                                                       HumanMessage("明天天气怎么样呢？")]})
rprint(prompt_template_invoke)
