import asyncio
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from utils import stream_response


async def demo() -> None:
    load_dotenv(override=True)

    llm_deepseek = init_chat_model(
        api_base=os.getenv("DEEPSEEK_API_BASE"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        model="deepseek-flash",
        model_provider="deepseek",
    )

    task = asyncio.create_task(llm_deepseek.ainvoke("解释一下人工智能"))

    for i in range(3):
        await asyncio.sleep(1)
    # 等待模型返回结果
    response = await task
    print("AI回复:", response.content)

async def main() -> None:
    await demo()

if __name__ == "__main__":
    asyncio.run(main())
