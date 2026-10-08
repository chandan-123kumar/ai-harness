# AI harness

A minimal Python coding-agent harness using `Qwen/Qwen3-Coder-Next` through
Hugging Face with the Novita backend. Includes conversation memory, a tool
registry, file operations, shell execution, and recursive text search.

Managed with [uv](https://docs.astral.sh/uv/guides/projects/). Python 3.10+ is
supported; `.python-version` selects Python 3.13 for local development.

```sh
uv sync
uv run cli.py
```

Use a Hugging Face token with **Make calls to Inference Providers** permission.
Before running the CLI, set the token in `.env` alongside `inference.py`:

```dotenv
HF_TOKEN=your_hugging_face_token
```

The CLI loads this file automatically. An existing `HF_TOKEN` environment
variable takes precedence. `.env` is ignored by Git. Never put a real token in
source code or chat.
Check your HF account credits/billing before use.

`pyproject.toml` declares dependencies. The first successful `uv sync` creates
`.venv` and `uv.lock`, which locks the resolved versions. Commit `uv.lock` once
generated, then use `uv sync --locked` for reproducible installs. `uv run` uses
the project's `.venv`; manual activation is not needed. Add dependencies with
`uv add <package>`.

Run offline checks:

```sh
uv run python -m unittest -v test_tools
```

`connect.py` is a separate single-request connection check. Its `config.json`
controls the model, provider, output limit, and timeout. These settings do not
configure the interactive `cli.py` loop. Ripgrep (`rg`) must be installed
separately for the search tool.

On 2026-10-05, the [HF provider catalog](https://huggingface.co/inference/models)
listed Novita at $0.20 per million input tokens and $1.50 per million output
tokens, with tool calling supported. Prices may change. The
[model](https://huggingface.co/Qwen/Qwen3-Coder-Next) uses Apache 2.0.
Tool dispatch is implemented; a saved live model/tool/model trace is still pending.
