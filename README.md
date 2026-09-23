# LangChain Demo

一个用于学习 LangChain / LangGraph 的示例项目，覆盖模型初始化与调用、消息与流式输出、多模态、Prompt 模板、结构化输出、工具调用、Agent、中间件、钩子（hooks）、记忆与持久化，以及 Langfuse / LangSmith 可观测性等主题。示例主要围绕 DeepSeek 模型展开。

## 项目结构

```text
.
├── charpter02/                        # 模型初始化与调用
│   ├── 01-model-init.py                     # ChatDeepSeek 直接初始化
│   ├── 02-model-init-ChatOpenAi.py          # OpenAI 兼容接口
│   ├── 03-init-chat-model.py                # init_chat_model 通用初始化
│   ├── 04-model-invoke.py                   # 多轮对话消息调用
│   ├── 05-streamAndBatch.py                 # 流式输出
│   ├── 06-model-ainvoke.py                  # 异步调用 ainvoke
│   ├── 07-model-profile-config.py           # 模型 profile 与完整参数
│   ├── 08-model_kwargs.py                   # 通过 model_kwargs 传入工具
│   └── utils.py                             # 公共工具函数
├── charpter03/                        # 可观测性（trace 日志）
│   └── 01-langfuse.py                       # Langfuse 集成
├── charpter04/                        # 对话、多模态与 Prompt
│   ├── 01-chatbot.py                        # 命令行聊天机器人
│   ├── 02-cotent-contentblocks.py           # 多模态（图片输入）
│   ├── 03-promptTemplate.py                 # ChatPromptTemplate 使用
│   ├── 04-promptTemplate-partial.py         # partial 与 MessagesPlaceholder
│   ├── Templates.py                         # 可复用提示词模板库
│   └── SpongeBob_SquarePants_character.png
├── charpter05/                        # 工具调用
│   ├── 01-tools.py                          # @tool 装饰器与 bind_tools
│   └── 02-toolchoice.py                     # tool_choice 与重试
├── charpter06/                        # 结构化数据（Notebook）
│   ├── 01-pydantic.ipynb                    # Pydantic 模型
│   ├── 02-typedict.ipynb                    # TypedDict
│   ├── 03-jsonschema.ipynb                  # JSON Schema
│   └── 04-dataclass.ipynb                   # dataclass
├── charpter07/                        # Agent 基础与结构化输出
│   ├── 01-agentbase.ipynb                   # create_agent 基础与流式
│   ├── 02-agent 结构化输出.ipynb             # 结构化输出的多种策略
│   └── 03-functionalagent.py                # 多功能工具 Agent
├── charpter08-middleware/             # 中间件
│   ├── 01-summarizationmiddleware.ipynb     # 对话摘要
│   ├── 02-HumanInTheLoopMiddleware.ipynb    # 人工介入
│   ├── 03-PIIMiddleware.ipynb               # 敏感信息处理
│   ├── 04-TodoListMiddleware.ipynb          # 待办清单
│   └── 05-codeagent.ipynb                   # 代码修复 Agent
├── charpter09-hooks/                  # 钩子（Hooks）
│   ├── 01-Node-Style-Hook.ipynb             # 节点式钩子
│   └── 02-Warp-Style-Hook.ipynb             # 包裹式钩子
├── charpter10-memery/                 # 记忆与持久化
│   ├── 01-ShortMemery.ipynb                 # 短期记忆（内存 / SQLite）
│   ├── 02-LongMemery.ipynb                  # 长期记忆（PostgreSQL）
│   └── 02-记忆治理策略.ipynb                 # 记忆压缩与删除
├── pyproject.toml
├── uv.lock
├── .env.template                            # 环境变量模板
├── LICENSE
└── README.md
```

> 注意：目录名当前为 `charpter02`（原拼写如此），运行命令时请使用项目里的实际拼写。

## 环境要求

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/)
- DeepSeek API Key
- Langfuse 账号（可选，用于 `charpter03` 的 trace 日志）
- PostgreSQL（可选，用于 `charpter10` 的长期记忆示例）

项目依赖定义在 `pyproject.toml` 中，主要包括：

- `langchain`、`langchain-core`
- `langchain-deepseek`、`langchain-openai`、`langchain-ollama`、`langchain-openrouter`
- `langgraph-checkpoint-sqlite`、`langgraph-checkpoint-postgres`、`psycopg`
- `langchain-tavily` / `tavily`（联网搜索工具）
- `langfuse`
- `pydantic-ai`、`pydantic-ai-harness`
- `python-dotenv`、`rich`、`jupyter`、`pytest`

## 安装依赖

在项目根目录执行：

```bash
uv sync
```

如果还没有安装 `uv`，可以参考官方安装方式，或先使用你本机已有的 Python 包管理工具安装。

## 配置环境变量

项目使用 `python-dotenv` 从 `.env` 文件读取环境变量。可以复制模板再填写：

```bash
cp .env.template .env
```

`.env` 内容示例：

```env
## deepseek
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_API_KEY=你的 DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com

## langsmith（可选）
#LANGSMITH_API_KEY=
#LANGSMITH_TRACING=true
#LANGCHAIN_TRACING_V2=true
#LANGSMITH_ENDPOINT=https://api.smith.langchain.com
#LANGSMITH_PROJECT=langc-demo

## langfuse（可选，charpter03 使用）
LANGFUSE_SECRET_KEY=你的 Langfuse Secret Key
LANGFUSE_PUBLIC_KEY=你的 Langfuse Public Key
LANGFUSE_BASE_URL=https://us.cloud.langfuse.com

## PostgreSQL（可选，charpter10 长期记忆使用）
DB_USER=admin
DB_PASSWORD=admin
DB_NAME=memery
DATABASE_URL=postgresql://admin:admin@localhost:5432/memery?sslmode=disable
```

说明：

- `DEEPSEEK_API_BASE`：`init_chat_model` 示例中使用。
- `DEEPSEEK_API_KEY`：DeepSeek API 密钥。
- `DEEPSEEK_BASE_URL`：`charpter02/02-model-init-ChatOpenAi.py` 通过它读取 OpenAI 兼容接口地址。
- `DATABASE_URL`：`charpter10` 长期记忆（`PostgresSaver`）的连接串。
- 如需使用 LangSmith 做 trace，可取消 `.env` 中 `LANGSMITH_*` 的注释。

`.env` 已加入 `.gitignore`，请不要把真实密钥提交到仓库。

## 运行示例

### charpter02：模型初始化与调用（脚本）

```bash
uv run python charpter02/01-model-init.py            # ChatDeepSeek 直接初始化
uv run python charpter02/02-model-init-ChatOpenAi.py # OpenAI 兼容接口
uv run python charpter02/03-init-chat-model.py       # init_chat_model 通用初始化
uv run python charpter02/04-model-invoke.py          # 多轮对话（输入 /quit 退出）
uv run python charpter02/05-streamAndBatch.py        # 流式输出与 batch
uv run python charpter02/06-model-ainvoke.py         # 异步调用 ainvoke
uv run python charpter02/07-model-profile-config.py  # 模型 profile 与完整参数
uv run python charpter02/08-model_kwargs.py          # 通过 model_kwargs 传入工具
```

- `04`：使用 `SystemMessage` / `HumanMessage` / `AIMessage` 维护上下文进行多轮对话。
- `05`：演示 `stream()` 流式输出，并借助 `utils.stream_response` 打印思考过程（`reasoning_content`）与正文。
- `06`：演示使用 `asyncio` 与 `ainvoke()` 进行异步调用。
- `07`：展示 LangChain 1.1+ 的模型 `profile` 以及 `ChatDeepSeek` 支持的完整字段。
- `08`：在 `model_kwargs` 中声明工具，完成「模型判断调用工具 → 执行工具 → 回传结果」的流程。

### charpter03：Langfuse 可观测性

```bash
uv run python charpter03/01-langfuse.py
```

通过 `langfuse.langchain.CallbackHandler` 将每次模型调用的 trace 上报到 Langfuse，可在 Web UI 查看调用链路、耗时与 token 用量。

### charpter04：对话、多模态与 Prompt

```bash
uv run python charpter04/01-chatbot.py                # 命令行聊天机器人（流式）
uv run python charpter04/02-cotent-contentblocks.py   # 多模态：图片输入
uv run python charpter04/03-promptTemplate.py         # ChatPromptTemplate
uv run python charpter04/04-promptTemplate-partial.py # partial 与 MessagesPlaceholder
```

- `01`：带系统人设的交互式聊天机器人。
- `02`：使用 `content_blocks` 传入图片（base64）实现多模态识别。
- `03` / `04`：演示 `ChatPromptTemplate`、`partial` 预填充与 `MessagesPlaceholder` 历史消息注入。

### charpter05：工具调用

```bash
uv run python charpter05/01-tools.py        # @tool 装饰器 + bind_tools
uv run python charpter05/02-toolchoice.py   # tool_choice 与重试
```

使用 `@tool` 装饰器把普通函数封装为可调用工具，并通过 `model.bind_tools()` 让模型自主决定是否调用（配合 `tool_choice="auto"`）。`02` 还演示了 `tenacity` 重试机制。

### charpter06：结构化数据（Notebook）

| Notebook | 主题 |
| --- | --- |
| `01-pydantic.ipynb` | Pydantic 模型、校验、别名与 `ConfigDict` |
| `02-typedict.ipynb` | `TypedDict` 定义结构 |
| `03-jsonschema.ipynb` | JSON Schema |
| `04-dataclass.ipynb` | `dataclass` |

### charpter07：Agent 基础与结构化输出（Notebook / 脚本）

- `01-agentbase.ipynb`：`create_agent` 基础、工具绑定与流式输出。
- `02-agent 结构化输出.ipynb`：结构化输出的多种策略、运行时校验与错误处理。
- `03-functionalagent.py`：多功能工具 Agent（天气 / 汇率 / 联网搜索 / 股票）并支持流式：

  ```bash
  uv run python charpter07/03-functionalagent.py
  ```

### charpter08-middleware：中间件（Notebook）

| Notebook | 主题 |
| --- | --- |
| `01-summarizationmiddleware.ipynb` | 对话摘要（`SummarizationMiddleware`） |
| `02-HumanInTheLoopMiddleware.ipynb` | 人工介入（`interrupt_on`、approve/edit/reject） |
| `03-PIIMiddleware.ipynb` | 敏感信息识别与脱敏 |
| `04-TodoListMiddleware.ipynb` | 待办清单管理 |
| `05-codeagent.ipynb` | 代码修复 Agent（工作区在 `./temp/`） |

### charpter09-hooks：钩子（Notebook）

| Notebook | 主题 |
| --- | --- |
| `01-Node-Style-Hook.ipynb` | 节点式钩子（`before_/after_agent`、`before_/after_model`、`dynamic_prompt` 等） |
| `02-Warp-Style-Hook.ipynb` | 包裹式钩子（`wrap_model_call`、`wrap_tool_call`） |

### charpter10-memery：记忆与持久化（Notebook）

| Notebook | 主题 |
| --- | --- |
| `01-ShortMemery.ipynb` | 短期记忆：`InMemorySaver` 与持久化 `SqliteSaver` / `AsyncSqliteSaver` |
| `02-LongMemery.ipynb` | 长期记忆：基于 PostgreSQL 的 `PostgresSaver` |
| `02-记忆治理策略.ipynb` | 记忆治理：压缩（摘要）与删除（滑动窗口 / token 裁剪 / 精确删除） |

> 持久化示例会把数据库文件写入 `temp/`（已加入 `.gitignore`）。

## 运行 Jupyter Notebook

用 PyCharm 打开 `.ipynb` 直接运行，或使用命令行：

```bash
uv run jupyter lab
```

注意事项：

- 请确保 Notebook 使用的内核是项目的 `.venv`（`Python 3 (ipykernel)`，解释器为 `.venv/bin/python`）。
- 执行过 `uv add` / `uv sync` 后，请**重启内核（Restart Kernel）**，否则新安装的包可能无法导入。

## 常见问题

### 找不到 API Key

请确认 `.env` 文件位于项目根目录，并且变量名与代码中读取的名称一致。

### `DEEPSEEK_API_BASE` 和 `DEEPSEEK_BASE_URL` 有什么区别？

这是不同示例脚本使用的两个变量名：

- `03-init-chat-model.py` 等使用 `DEEPSEEK_API_BASE`
- `02-model-init-ChatOpenAi.py` 使用 `DEEPSEEK_BASE_URL`

### 报错 `Thinking mode does not support this tool_choice`

DeepSeek 的思考模式不支持强制 `tool_choice`。本项目在初始化模型时统一传入 `model_kwargs={"reasoning_effort": "none"}` 关闭思考模式，涉及强制工具选择或结构化输出时请保持该设置。

### 重启后仍报 `ModuleNotFoundError`

通常是内核是旧进程导致的。请重启 Notebook 内核；若仍失败，确认内核解释器指向 `.venv/bin/python`。

### `PostgresSaver` 导入报 `no pq wrapper available` / `libpq library not found`

`psycopg` 需要 libpq 运行时。安装二进制包即可（已包含在依赖中）：

```bash
uv add psycopg-binary
```

此外还需要一个可连接的 PostgreSQL 实例，并正确设置 `DATABASE_URL`。

### 为什么有 `uv.lock`？

`uv.lock` 是 uv 生成的依赖锁定文件，用于记录精确的依赖版本，保证不同环境安装到一致的包版本。通常建议提交到版本库。

## 后续可扩展示例

- 批量调用 `batch()`
- LCEL 链式调用
- RAG 检索增强生成
- 多智能体编排

## License

本项目基于 [MIT License](LICENSE) 开源。
