import json
import urllib.parse
import urllib.request

from langchain_core.messages import AIMessage


def get_weather(city: str) -> str:
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


def _content_to_text(content) -> str:
    """把 LangChain chunk 中可能出现的不同 content 格式统一转成字符串。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in content
        )
    if content is None:
        return ""
    return str(content)


def print_response(response: AIMessage) -> None:
    """按常用字段打印 AIMessage，避免直接输出完整对象。"""
    print("\n========== AI 回复 ==========")
    print(response.content)

    reasoning_content = response.additional_kwargs.get("reasoning_content")
    if reasoning_content:
        print("\n========== 推理内容 ==========")
        print(reasoning_content)

    usage = response.usage_metadata or {}
    if usage:
        print("\n========== Token 用量 ==========")
        print(f"输入 tokens：{usage.get('input_tokens')}")
        print(f"输出 tokens：{usage.get('output_tokens')}")
        print(f"总 tokens：{usage.get('total_tokens')}")

        output_token_details = usage.get("output_token_details") or {}
        reasoning_tokens = output_token_details.get("reasoning")
        if reasoning_tokens is not None:
            print(f"推理 tokens：{reasoning_tokens}")

    metadata = response.response_metadata or {}
    if metadata:
        print("\n========== 响应信息 ==========")
        print(f"模型服务商：{metadata.get('model_provider')}")
        print(f"模型名称：{metadata.get('model_name')}")
        print(f"结束原因：{metadata.get('finish_reason')}")
        print(f"响应 ID：{metadata.get('id')}")

    print()


def stream_response(chunks) -> AIMessage:
    """流式打印 reasoning_content 和 content，并返回可加入上下文的 AIMessage。"""
    # 流式响应会分成很多小片段返回，这里分别收集最终回复和思考过程。
    content_parts = []
    reasoning_parts = []

    # response_chunk 用来尝试合并所有 chunk，保留 LangChain 附带的额外字段。
    response_chunk = None

    # 控制标题只打印一次，避免每个 chunk 都重复输出标题。
    has_printed_reasoning_header = False
    has_printed_answer_header = False

    for chunk in chunks:
        # 部分 LangChain 消息 chunk 支持相加，用于合并成一个完整响应。
        if response_chunk is None:
            response_chunk = chunk
        else:
            try:
                response_chunk += chunk
            except TypeError:
                # 如果当前 chunk 类型不支持相加，不影响正文和思考过程的流式输出。
                pass

        # DeepSeek 的思考过程通常放在 additional_kwargs["reasoning_content"] 中。
        reasoning_content = chunk.additional_kwargs.get("reasoning_content")
        if reasoning_content:
            if not has_printed_reasoning_header:
                print("\n========== 思考过程 ==========")
                has_printed_reasoning_header = True
            print(reasoning_content, end="", flush=True)
            reasoning_parts.append(reasoning_content)

        # 普通回复内容在 chunk.content 中，边收到边打印，实现流式输出效果。
        content = _content_to_text(chunk.content)
        if content:
            if not has_printed_answer_header:
                if has_printed_reasoning_header:
                    print()
                print("\n========== AI 回复 ==========")
                has_printed_answer_header = True
            print(content, end="", flush=True)
            content_parts.append(content)

    print()

    # 构造一个完整的 AIMessage，方便调用方追加到 messages，继续多轮对话。
    additional_kwargs = {}
    if reasoning_parts:
        additional_kwargs["reasoning_content"] = "".join(reasoning_parts)

    # 合并 LangChain 保留的额外字段，例如模型服务返回的特殊元数据。
    if response_chunk is not None:
        additional_kwargs.update(response_chunk.additional_kwargs)

    return AIMessage(
        content="".join(content_parts),
        additional_kwargs=additional_kwargs,
    )
