"""多功能 Agent 示例。

包含四个工具（全部无需 API Key）：
1. get_weather      —— 查询城市实时天气（Open-Meteo）
2. convert_currency —— 货币汇率换算（open.er-api.com，回退 frankfurter）
3. web_search       —— 联网搜索（Bing，回退 DuckDuckGo Instant Answer / Wikipedia）
4. get_stock_price  —— 股票行情（腾讯行情接口，支持 A 股 / 港股 / 美股，可传代码或名称）

运行：
    uv run python charpter07/03-functionalagent.py
"""

import base64
import json
import os
import re
import urllib.parse
import urllib.request
from typing import Annotated, Literal

from IPython.display import Image,display
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

# ---------------------------------------------------------------------------
# 通用 HTTP 辅助函数
# ---------------------------------------------------------------------------
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


def _request(url: str, *, headers: dict | None = None, timeout: int = 15) -> bytes:
    """发起 GET 请求并返回原始字节。"""
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _get_text(url: str, *, encoding: str = "utf-8", headers: dict | None = None, timeout: int = 15) -> str:
    """GET 请求并按指定编码解码为字符串。"""
    return _request(url, headers=headers, timeout=timeout).decode(encoding, "ignore")


def _get_json(url: str, *, headers: dict | None = None, timeout: int = 15):
    """GET 请求并解析为 JSON。"""
    return json.loads(_get_text(url, headers=headers, timeout=timeout))


def _dumps(obj) -> str:
    """统一以对中文友好的 JSON 字符串返回工具结果。"""
    return json.dumps(obj, ensure_ascii=False)


# ---------------------------------------------------------------------------
# 工具 1：天气查询
# ---------------------------------------------------------------------------
@tool
def get_weather(
    city: Annotated[str, "城市名称，如北京、上海、深圳"],
    unit: Annotated[Literal["celsius", "fahrenheit"], "温度单位"] = "celsius",
) -> str:
    """查询指定城市的实时天气，返回温度、湿度和风速。"""
    # 第一步：用城市名查经纬度
    geo_url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode(
        {"name": city, "count": 1, "language": "zh", "format": "json"}
    )
    geo = _get_json(geo_url)
    results = geo.get("results") or []
    if not results:
        return _dumps({"error": f"没有找到城市：{city}"})

    location = results[0]

    # 第二步：用经纬度查实时天气
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "timezone": "auto",
    }
    if unit == "fahrenheit":
        params["temperature_unit"] = "fahrenheit"
    weather = _get_json(
        "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
    )

    current = weather.get("current", {})
    units = weather.get("current_units", {})
    return _dumps(
        {
            "city": location.get("name"),
            "country": location.get("country"),
            "temperature": current.get("temperature_2m"),
            "temperature_unit": units.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "humidity_unit": units.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "wind_speed_unit": units.get("wind_speed_10m"),
        }
    )


# ---------------------------------------------------------------------------
# 工具 2：汇率换算
# ---------------------------------------------------------------------------
def _currency_result(amount: float, base: str, target: str, rate: float, date) -> str:
    """拼装统一的汇率换算结果。"""
    return _dumps(
        {
            "amount": amount,
            "from": base,
            "to": target,
            "rate": rate,
            "converted": round(amount * rate, 4),
            "update_time": date,
        }
    )


@tool
def convert_currency(
    amount: Annotated[float, "要换算的金额"],
    from_currency: Annotated[str, "源货币代码，如 USD、CNY、EUR"],
    to_currency: Annotated[str, "目标货币代码，如 CNY、USD、JPY"],
) -> str:
    """按实时汇率把一种货币换算成另一种货币。"""
    base = from_currency.strip().upper()
    target = to_currency.strip().upper()

    # 首选 open.er-api.com：支持币种多，无需 Key
    try:
        data = _get_json(f"https://open.er-api.com/v6/latest/{base}")
        if data.get("result") == "success":
            rate = data.get("rates", {}).get(target)
            if rate is not None:
                return _currency_result(
                    amount, base, target, rate, data.get("time_last_update_utc")
                )
    except Exception:
        pass

    # 回退 frankfurter（欧洲央行数据，支持常见货币）
    try:
        data = _get_json(
            f"https://api.frankfurter.dev/v1/latest?base={base}&symbols={target}"
        )
        rate = data.get("rates", {}).get(target)
        if rate is not None:
            return _currency_result(amount, base, target, rate, data.get("date"))
    except Exception:
        pass

    return _dumps({"error": f"无法获取 {base} -> {target} 的汇率，请检查货币代码"})


# ---------------------------------------------------------------------------
# 工具 3：联网搜索
# ---------------------------------------------------------------------------
def _decode_bing_url(href: str) -> str:
    """把 Bing 的跳转链接还原成真实 URL。"""
    if not href:
        return href
    query = urllib.parse.urlparse(href).query
    u = urllib.parse.parse_qs(query).get("u", [None])[0]
    if not u:
        return href
    # Bing 的 u 参数形如 a1<base64url>，去掉前缀后做 base64 解码
    token = u[2:] if u.startswith("a1") else u
    token = token.replace("-", "+").replace("_", "/")
    token += "=" * (-len(token) % 4)
    try:
        return base64.b64decode(token).decode("utf-8", "ignore")
    except Exception:
        return href


def _search_bing(query: str, max_results: int) -> list[dict]:
    """抓取 Bing 网页搜索结果。"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    url = "https://www.bing.com/search?" + urllib.parse.urlencode({"q": query})
    html = _get_text(
        url, headers={"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}
    )
    soup = BeautifulSoup(html, "html.parser")

    results = []
    for li in soup.select("li.b_algo"):
        link = li.select_one("h2 a")
        if link is None:
            continue
        snippet_el = li.select_one("p")
        results.append(
            {
                "title": link.get_text(" ", strip=True),
                "url": _decode_bing_url(link.get("href", "")),
                "snippet": snippet_el.get_text(" ", strip=True) if snippet_el else "",
            }
        )
        if len(results) >= max_results:
            break
    return results


def _search_duckduckgo(query: str, max_results: int) -> list[dict]:
    """DuckDuckGo Instant Answer API（返回摘要与相关主题）。"""
    url = "https://api.duckduckgo.com/?" + urllib.parse.urlencode(
        {"q": query, "format": "json", "no_html": 1, "no_redirect": 1}
    )
    data = _get_json(url)

    results = []
    if data.get("AbstractText"):
        results.append(
            {
                "title": data.get("Heading") or query,
                "url": data.get("AbstractURL", ""),
                "snippet": data.get("AbstractText", ""),
            }
        )
    for topic in data.get("RelatedTopics", []):
        if len(results) >= max_results:
            break
        if isinstance(topic, dict) and topic.get("Text"):
            results.append(
                {
                    "title": topic.get("Text", "")[:60],
                    "url": topic.get("FirstURL", ""),
                    "snippet": topic.get("Text", ""),
                }
            )
    return results[:max_results]


def _search_wikipedia(query: str, max_results: int) -> list[dict]:
    """维基百科搜索（先中文，后英文）。"""
    for lang in ("zh", "en"):
        url = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
            {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "utf8": 1,
                "srlimit": max_results,
            }
        )
        data = _get_json(url)
        hits = data.get("query", {}).get("search", [])
        if hits:
            return [
                {
                    "title": hit.get("title", ""),
                    "url": f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(hit.get('title', ''))}",
                    "snippet": re.sub(r"<[^>]+>", "", hit.get("snippet", "")),
                }
                for hit in hits[:max_results]
            ]
    return []


@tool
def web_search(
    query: Annotated[str, "搜索关键词"],
    max_results: Annotated[int, "返回结果条数"] = 5,
) -> str:
    """联网搜索，返回标题、链接和摘要。"""
    results: list[dict] = []
    # 依次尝试多个来源，任意一个成功即返回
    for searcher in (_search_bing, _search_duckduckgo, _search_wikipedia):
        try:
            results = searcher(query, max_results)
        except Exception:
            results = []
        if results:
            break

    if not results:
        return _dumps({"query": query, "error": "未找到相关结果，请更换关键词重试"})
    return _dumps({"query": query, "results": results})


# ---------------------------------------------------------------------------
# 工具 4：股票行情
# ---------------------------------------------------------------------------
def _to_quote_code(market: str, raw_code: str) -> str:
    """把行情接口返回的市场/代码转换成腾讯行情接口用的完整代码。"""
    market = market.lower()
    if market == "us":
        # 美股去掉 .oq / .n 等后缀并转大写，例如 aapl.oq -> usAAPL
        return "us" + raw_code.split(".")[0].upper()
    return f"{market}{raw_code}"


def _normalize_stock_symbol(symbol: str) -> str | None:
    """把用户输入的代码规范化成行情接口代码；不是代码则返回 None。"""
    s = symbol.strip()
    low = s.lower()

    # 已带市场前缀，如 sh600519 / hk00700 / usAAPL
    if low[:2] in {"sh", "sz", "hk", "us"}:
        return low

    # 纯数字：5 位是港股，6 位是 A 股（6/9 开头沪市，其余深市）
    if s.isdigit():
        if len(s) == 5:
            return "hk" + s
        if len(s) == 6:
            return ("sh" if s[0] in "69" else "sz") + s

    # 纯字母视为美股代码
    if re.fullmatch(r"[A-Za-z][A-Za-z.\-]{0,9}", s):
        return "us" + s.split(".")[0].upper()

    return None


def _search_stock(keyword: str) -> list[dict]:
    """按名称搜索股票代码（腾讯 smartbox）。"""
    url = "https://smartbox.gtimg.cn/s3/?" + urllib.parse.urlencode(
        {"q": keyword, "t": "all"}
    )
    text = _get_text(url)
    if '="' not in text:
        return []

    inner = text.split('="', 1)[1].rstrip('";\n')
    matches = []
    for entry in inner.split("^"):
        fields = entry.split("~")
        if len(fields) < 3:
            continue
        market, raw_code, name = fields[0], fields[1], fields[2]
        kind = fields[4] if len(fields) > 4 else ""
        try:
            name = json.loads(f'"{name}"')  # 解码 \uXXXX 形式的名称
        except Exception:
            pass
        matches.append(
            {
                "name": name,
                "code": _to_quote_code(market, raw_code),
                "kind": kind,
            }
        )

    # 排序：名称完全匹配 > 股票（GP）> 名称包含关键词，让最相关的结果排在前面
    def _rank(match: dict) -> tuple:
        return (
            match["name"] == keyword,
            match["kind"].startswith("GP"),
            keyword in match["name"],
        )

    matches.sort(key=_rank, reverse=True)
    return matches


def _fetch_quote(code: str) -> dict | None:
    """调用腾讯行情接口获取最新报价。"""
    text = _get_text(f"https://qt.gtimg.cn/q={code}", encoding="gbk")
    if '="' not in text:
        return None

    parts = text.split('="', 1)[1].rstrip('";\n').split("~")
    if len(parts) < 35:
        return None

    def num(index: int) -> float | None:
        try:
            return float(parts[index])
        except (ValueError, IndexError):
            return None

    return {
        "code": parts[2],
        "name": parts[1],
        "price": num(3),
        "prev_close": num(4),
        "open": num(5),
        "high": num(33),
        "low": num(34),
        "change": num(31),
        "change_percent": num(32),
        "volume": parts[6],
        "time": parts[30],
    }


@tool
def get_stock_price(
    symbol: Annotated[str, "股票代码或名称，如 600519、00700、AAPL、贵州茅台、腾讯"],
) -> str:
    """查询股票实时行情，支持 A 股、港股、美股；可传代码或公司名称。"""
    code = _normalize_stock_symbol(symbol)

    # 不是代码，就按名称搜索出最匹配的代码
    if code is None:
        matches = _search_stock(symbol)
        if not matches:
            return _dumps({"error": f"没有找到股票：{symbol}"})
        code = matches[0]["code"]

    quote = _fetch_quote(code)
    if quote is None:
        return _dumps({"error": f"没有查询到行情：{symbol}（解析代码 {code}）"})
    return _dumps(quote)


# ---------------------------------------------------------------------------
# 构建并运行 Agent
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "你是一个多功能助手，可以查询天气、换算汇率、联网搜索和查询股票行情。"
    "请根据用户的问题选择合适的工具，必要时可以连续调用多个工具，最后用简洁的中文回答。"
)


def build_agent():
    """初始化模型并创建多功能 Agent。"""
    load_dotenv(override=True)

    model = init_chat_model(
        api_base=os.getenv("DEEPSEEK_API_BASE"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        model=os.getenv("AGENT_MODEL", "deepseek-flash"),
        model_provider="deepseek",
    )

    return create_agent(
        model=model,
        tools=[get_weather, convert_currency, web_search, get_stock_price],
        system_prompt=SYSTEM_PROMPT,
    )


def _stream_agent(agent, messages):
    """以 messages 模式流式运行 Agent，实时打印思考过程与回答。

    返回最终 state，用于维护多轮对话上下文。
    """
    final_state = None
    printed_count = len(messages)   # 已处理过的消息数，避免重复打印历史工具调用
    thinking_started = False
    answer_started = False

    # 同时订阅两种模式：messages 用于逐 token 打印，values 用于拿到最终完整状态
    for mode, chunk in agent.stream(
        {"messages": messages},
        stream_mode=["messages", "values"],
    ):
        if mode == "values":
            final_state = chunk
            # 新出现的消息里如果带工具调用，就打印出来
            for msg in chunk["messages"][printed_count:]:
                for tool_call in getattr(msg, "tool_calls", None) or []:
                    print(f"\n  [调用工具] {tool_call['name']} {_dumps(tool_call['args'])}", end="")
            printed_count = len(chunk["messages"])
            continue

        # mode == "messages"：chunk 是 (message_chunk, metadata)
        message_chunk, metadata = chunk
        if metadata.get("langgraph_node") != "model":
            continue

        # DeepSeek 思考模型的思考过程
        reasoning = message_chunk.additional_kwargs.get("reasoning_content")
        if reasoning:
            if not thinking_started:
                print("\n[思考] ", end="")
                thinking_started = True
            print(reasoning, end="", flush=True)

        # 正文内容，边生成边打印
        if message_chunk.content:
            if not answer_started:
                if thinking_started:
                    print()
                print("\n[回答] ", end="")
                answer_started = True
            print(message_chunk.content, end="", flush=True)

    print()
    return final_state


def main():
    agent = build_agent()
    print("多功能 Agent 已启动，可查询天气 / 汇率 / 联网搜索 / 股票行情。")
    print("输入问题开始，输入 exit 退出。\n")
    display(Image(agent.get_graph().draw_mermaid_png()))

    messages = []
    while True:
        user_input = input("你：").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("再见！")
            break
        if not user_input:
            continue

        messages.append(HumanMessage(content=user_input))

        # 用 messages 模式流式运行并打印，最终状态用于维护多轮上下文
        final_state = _stream_agent(agent, messages)
        if final_state is not None:
            messages = final_state["messages"]


if __name__ == "__main__":
    main()
