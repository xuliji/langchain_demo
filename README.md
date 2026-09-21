# LangChain Demo

一个用于学习 LangChain 模型初始化与调用方式的示例项目。当前示例主要围绕 DeepSeek 模型，展示了直接使用 DeepSeek 集成、使用 OpenAI 兼容接口，以及通过 LangChain 通用初始化方法创建聊天模型。

## 项目结构

```text
.
├── charpter02/
│   ├── 01-model-init.py
│   ├── 02-model-init-ChatOpenAi.py
│   ├── 03-init-chat-model.py
│   └── 04-model-invoke.py
├── pyproject.toml
├── uv.lock
└── README.md
```

> 注意：目录名当前为 `charpter02`，运行命令时请使用项目里的实际拼写。

## 环境要求

- Python >= 3.14
- uv
- DeepSeek API Key

项目依赖定义在 `pyproject.toml` 中，主要包括：

- `langchain`
- `langchain-core`
- `langchain-deepseek`
- `langchain-openai`
- `python-dotenv`

## 安装依赖

在项目根目录执行：

```bash
uv sync
```

如果还没有安装 `uv`，可以参考官方安装方式，或先使用你本机已有的 Python 包管理工具安装。

## 配置环境变量

项目使用 `python-dotenv` 从 `.env` 文件读取环境变量。请在项目根目录创建 `.env` 文件：

```env
DEEPSEEK_API_KEY=你的 DeepSeek API Key
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

说明：

- `DEEPSEEK_API_KEY`：DeepSeek API 密钥。
- `DEEPSEEK_API_BASE`：`init_chat_model` 示例中使用。
- `DEEPSEEK_BASE_URL`：`ChatOpenAI` 兼容接口示例中使用。

`.env` 已加入 `.gitignore`，请不要把真实密钥提交到仓库。

## 运行示例

### 1. 使用 `langchain_deepseek.ChatDeepSeek`

```bash
uv run python charpter02/01-model-init.py
```

该示例直接使用 `langchain-deepseek` 提供的 `ChatDeepSeek` 初始化模型，并调用：

```python
response = llm_deepseek.invoke("uv.lock是什么文件？有什么作用")
```

### 2. 使用 OpenAI 兼容接口

```bash
uv run python charpter02/02-model-init-ChatOpenAi.py
```

该示例使用 `langchain_openai.ChatOpenAI`，通过 `base_url` 指向 DeepSeek 的 OpenAI 兼容 API。

### 3. 使用 LangChain 通用初始化方法

```bash
uv run python charpter02/03-init-chat-model.py
```

该示例使用：

```python
from langchain.chat_models import init_chat_model
```

并通过 `model_provider="deepseek"` 初始化 DeepSeek 聊天模型。

### 4. 模型调用示例

`charpter02/04-model-invoke.py` 当前为空文件，可用于后续补充模型调用、消息格式、多轮对话或流式输出等示例。

## 常见问题

### 找不到 API Key

请确认 `.env` 文件位于项目根目录，并且变量名与代码中读取的名称一致。

### `DEEPSEEK_API_BASE` 和 `DEEPSEEK_BASE_URL` 有什么区别？

这是当前不同示例脚本使用的两个变量名：

- `03-init-chat-model.py` 使用 `DEEPSEEK_API_BASE`
- `02-model-init-ChatOpenAi.py` 使用 `DEEPSEEK_BASE_URL`

如果希望减少混淆，可以后续统一变量名，并同步修改对应脚本。

### 为什么有 `uv.lock`？

`uv.lock` 是 uv 生成的依赖锁定文件，用于记录精确的依赖版本，保证不同环境安装到一致的包版本。通常建议提交到版本库。

## 后续可扩展示例

- 多轮对话消息调用
- 流式输出
- PromptTemplate 使用
- LCEL 链式调用
- 工具调用
- RAG 检索增强生成

