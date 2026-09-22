# LangChain Demo

一个用于学习 LangChain 的示例项目，覆盖模型初始化与调用、消息与流式输出、多模态、Prompt 模板、工具调用以及 Langfuse 可观测性等主题。当前示例主要围绕 DeepSeek 模型展开。

## 项目结构

```text
.
├── charpter02/                # 模型初始化与调用
│   ├── 01-model-init.py             # ChatDeepSeek 直接初始化
│   ├── 02-model-init-ChatOpenAi.py  # OpenAI 兼容接口
│   ├── 03-init-chat-model.py        # init_chat_model 通用初始化
│   ├── 04-model-invoke.py           # 多轮对话消息调用
│   ├── 05-streamAndBatch.py         # 流式输出
│   ├── 06-model-ainvoke.py          # 异步调用 ainvoke
│   ├── 07-model-profile-config.py   # 模型 profile 与完整参数
│   ├── 08-model_kwargs.py           # 通过 model_kwargs 传入工具
│   └── utils.py                     # 公共工具函数
├── charpter03/                # 可观测性（trace 日志）
│   └── 01-langfuse.py               # Langfuse 集成
├── charpter04/                # 对话、多模态与 Prompt
│   ├── 01-chatbot.py                # 命令行聊天机器人
│   ├── 02-cotent-contentblocks.py   # 多模态（图片输入）
│   ├── 03-promptTemplate.py         # ChatPromptTemplate 使用
│   ├── 04-promptTemplate-partial.py # partial 与 MessagesPlaceholder
│   ├── Templates.py                 # 可复用提示词模板库
│   └── SpongeBob_SquarePants_character.png
├── charpter05/                # 工具调用
│   ├── 01-tools.py                  # @tool 装饰器与 bind_tools
│   └── 02-toolchoice.py             # tool_choice 与重试
├── pyproject.toml
├── uv.lock
└── README.md
```

> 注意：目录名当前为 `charpter02`（原拼写如此），运行命令时请使用项目里的实际拼写。

## 环境要求

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/)
- DeepSeek API Key
- Langfuse 账号（可选，用于 `charpter03` 的 trace 日志）

项目依赖定义在 `pyproject.toml` 中，主要包括：

- `langchain`、`langchain-core`
- `langchain-deepseek`
- `langchain-openai`
- `langchain-ollama`
- `langchain-openrouter`
- `langfuse`
- `pydantic-ai`、`pydantic-ai-harness`
- `python-dotenv`
- `rich`
- `jupyter`

## 安装依赖

在项目根目录执行：

```bash
uv sync
```

如果还没有安装 `uv`，可以参考官方安装方式，或先使用你本机已有的 Python 包管理工具安装。

## 配置环境变量

项目使用 `python-dotenv` 从 `.env` 文件读取环境变量。请在项目根目录创建 `.env` 文件：

```env
## deepseek
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_API_KEY=你的 DeepSeek API Key

## langfuse（可选，charpter03 使用）
LANGFUSE_PUBLIC_KEY=你的 Langfuse Public Key
LANGFUSE_SECRET_KEY=你的 Langfuse Secret Key
LANGFUSE_BASE_URL=https://us.cloud.langfuse.com
```

说明：

- `DEEPSEEK_API_BASE`：`init_chat_model` 示例中使用。
- `DEEPSEEK_API_KEY`：DeepSeek API 密钥。
- `charpter02/02-model-init-ChatOpenAi.py` 通过 `DEEPSEEK_BASE_URL` 读取 OpenAI 兼容接口地址，如使用该脚本需自行补充该变量。
- 如需使用 LangSmith 做 trace，可参考 `.env` 中被注释的 `LANGSMITH_*` 配置。

`.env` 已加入 `.gitignore`，请不要把真实密钥提交到仓库。

## 运行示例

### 1. 使用 `langchain_deepseek.ChatDeepSeek`

```bash
uv run python charpter02/01-model-init.py
```

该示例直接使用 `langchain-deepseek` 提供的 `ChatDeepSeek` 初始化模型并调用。

### 2. 使用 OpenAI 兼容接口

```bash
uv run python charpter02/02-model-init-ChatOpenAi.py
```

该示例使用 `langchain_openai.ChatOpenAI`，通过 `base_url` 指向 DeepSeek 的 OpenAI 兼容 API。

### 3. 使用 LangChain 通用初始化方法

```bash
uv run python charpter02/03-init-chat-model.py
```

通过 `langchain.chat_models.init_chat_model`，指定 `model_provider="deepseek"` 初始化聊天模型。

### 4. 多轮对话消息调用

```bash
uv run python charpter02/04-model-invoke.py
```

演示使用 `SystemMessage` / `HumanMessage` / `AIMessage` 维护上下文，进行交互式多轮对话（输入 `/quit` 退出）。

### 5. 流式输出

```bash
uv run python charpter02/05-streamAndBatch.py
```

演示 `stream()` 流式输出，并借助 `utils.stream_response` 打印思考过程（`reasoning_content`）与正文。

### 6. 异步调用

```bash
uv run python charpter02/06-model-ainvoke.py
```

演示使用 `asyncio` 与 `ainvoke()` 进行异步调用。

### 7. 模型 profile 与参数

```bash
uv run python charpter02/07-model-profile-config.py
```

展示 LangChain 1.1+ 的模型 `profile` 以及 `ChatDeepSeek` 支持的完整字段。

### 8. 通过 model_kwargs 传入工具

```bash
uv run python charpter02/08-model_kwargs.py
```

演示直接在 `init_chat_model` 的 `model_kwargs` 中声明工具，并完成「模型判断调用工具 → 执行工具 → 回传结果」的完整流程。

## charpter03：Langfuse 可观测性

```bash
uv run python charpter03/01-langfuse.py
```

演示通过 `langfuse.langchain.CallbackHandler` 将每次模型调用的 trace 上报到 Langfuse，便于在 Web UI 中查看调用链路、耗时与 token 用量。

## charpter04：对话、多模态与 Prompt

```bash
uv run python charpter04/01-chatbot.py               # 命令行聊天机器人（流式）
uv run python charpter04/02-cotent-contentblocks.py  # 多模态：图片输入
uv run python charpter04/03-promptTemplate.py        # ChatPromptTemplate
uv run python charpter04/04-promptTemplate-partial.py # partial 与 MessagesPlaceholder
```

- `01-chatbot.py`：带系统人设的交互式聊天机器人。
- `02-cotent-contentblocks.py`：使用 `content_blocks` 传入图片（base64）实现多模态识别。
- `03-promptTemplate.py` / `04-promptTemplate-partial.py`：演示 `ChatPromptTemplate`、`partial` 预填充与 `MessagesPlaceholder` 历史消息注入。

## charpter05：工具调用

```bash
uv run python charpter05/01-tools.py        # @tool 装饰器 + bind_tools
uv run python charpter05/02-toolchoice.py   # tool_choice 与重试
```

演示使用 `@tool` 装饰器把普通函数封装为可调用工具，并通过 `model.bind_tools()` 让模型自主决定是否调用（配合 `tool_choice="auto"`）。`02` 还演示了 `tenacity` 重试机制。

## 常见问题

### 找不到 API Key

请确认 `.env` 文件位于项目根目录，并且变量名与代码中读取的名称一致。

### `DEEPSEEK_API_BASE` 和 `DEEPSEEK_BASE_URL` 有什么区别？

这是不同示例脚本使用的两个变量名：

- `03-init-chat-model.py` 等使用 `DEEPSEEK_API_BASE`
- `02-model-init-ChatOpenAi.py` 使用 `DEEPSEEK_BASE_URL`

当前 `.env` 仅配置了 `DEEPSEEK_API_BASE`，如运行 `02` 需补充 `DEEPSEEK_BASE_URL`，也可后续统一变量名。

### 为什么有 `uv.lock`？

`uv.lock` 是 uv 生成的依赖锁定文件，用于记录精确的依赖版本，保证不同环境安装到一致的包版本。通常建议提交到版本库。

## 后续可扩展示例

- 批量调用 `batch()`
- LCEL 链式调用
- RAG 检索增强生成
- 多智能体编排
