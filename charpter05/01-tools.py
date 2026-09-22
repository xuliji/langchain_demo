import urllib.parse
import urllib.request
import json
from typing import Literal

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import BaseModel, Field
from rich import print as rprint

class WeatherInput(BaseModel):
    city: str = Field(
        description="具体的城市",
        default="北京"
    )
    unit: Literal["celsius", "fahrenheit"]
@tool(args_schema=WeatherInput)
def get_weather(city:str, unit:str="celsius")->str:
    """
    获取指定城市的天气信息

    :param city: 城市名称 如北京，上海
    :return: 天气信息字符串
    """
    """调用 Open-Meteo API 查询城市天气。"""
    # 第一步：用城市名称查经纬度。
    geo_params = urllib.parse.urlencode(
        {
            "name": city,
            "count": 1,
            "language": "zh",
            "format": "json",
        }
    )
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?{geo_params}"

    with urllib.request.urlopen(geo_url, timeout=10) as response:
        geo_data = json.loads(response.read().decode("utf-8"))

    results = geo_data.get("results") or []
    if not results:
        return json.dumps({"error": f"没有找到城市：{city}"}, ensure_ascii=False)

    location = results[0]
    latitude = location["latitude"]
    longitude = location["longitude"]

    # 第二步：用经纬度查当前天气。
    weather_params = urllib.parse.urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            "timezone": "auto",
        }
    )
    weather_url = f"https://api.open-meteo.com/v1/forecast?{weather_params}"

    with urllib.request.urlopen(weather_url, timeout=10) as response:
        weather_data = json.loads(response.read().decode("utf-8"))

    current = weather_data.get("current", {})
    current_units = weather_data.get("current_units", {})

    return json.dumps(
        {
            "city": location.get("name"),
            "country": location.get("country"),
            "temperature": current.get("temperature_2m"),
            "temperature_unit": current_units.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "humidity_unit": current_units.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "wind_speed_unit": current_units.get("wind_speed_10m"),
        },
        ensure_ascii=False,
    )

## 直接调用
# rprint(get_weather.invoke({"city":"上海"}))

## 模型调用

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


model_bind_tools = model.bind_tools([get_weather])
messages = [
    HumanMessage("上海今天天气怎么样？")
]
response = model_bind_tools.invoke(messages)
messages.append(response)
if response.tool_calls:
    for tool_call in response.tool_calls:
        if tool_call["name"] == "get_weather":
            tool_result = get_weather.invoke(tool_call)
            print(type(tool_result))
            messages.append(tool_result)

rprint(model_bind_tools.invoke(messages))

rprint(convert_to_openai_tool(get_weather))