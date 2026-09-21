## 多模态
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from rich import print as rprint

from charpter02.utils import *

load_dotenv(override=True)

model = init_chat_model(
    api_base=os.getenv("DEEPSEEK_API_BASE"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-flash",
    model_provider="deepseek",
)

messages = [
    SystemMessage(content="你是杀生鱼丸 请用杀生鱼丸的口吻和我对话 要俏皮一点的"),
    # HumanMessage(content=[
    #     {'type': 'text', 'text': '这是谁？'},
    #     {
    #         'type': 'image_url',
    #         "image_url": {"url": encode_image("./SpongeBob_SquarePants_character.png")}
    #     }
    # ])
    HumanMessage(content_blocks=[
        {'type': 'text', 'text': '这是谁？'},
        {
            'type': 'image',
            "base64": encode_image("./SpongeBob_SquarePants_character.png"),
            'mime_type': 'image/png',
        }
    ])
]

stream_response(model.stream(messages))
