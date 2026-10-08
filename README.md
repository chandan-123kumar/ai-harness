# Karyo

A terminal coding assistant using `Qwen/Qwen3-Coder-Next` through Hugging Face's
Novita provider. Includes conversation memory, file operations, shell execution,
and recursive text search.

## Install

On **macOS, Linux, or Windows with WSL**, run:

```sh
curl -fsSL https://raw.githubusercontent.com/chandan-123kumar/karyo/main/install.sh | sh
```

The installer installs [uv](https://docs.astral.sh/uv/), provisions Python 3.13
if needed, installs the `karyo` command, and opens a browser setup page.
Paste your own [Hugging Face token](https://huggingface.co/settings/tokens) with
**Make calls to Inference Providers** permission and click **Save token and continue**.
Hugging Face inference credits/billing are required.

Open a new terminal after installation:

```sh
cd your-project
karyo
```

Type `/exit` or press Ctrl+C to quit. This agent can write files and execute shell
commands with your user permissions; use it in projects you trust and keep backups.
Native Windows is not supported by the shell tool; use WSL.

Already have uv? Install directly:

```sh
uv tool install --python 3.13 --from https://github.com/chandan-123kumar/karyo/archive/refs/heads/main.zip karyo
uv tool update-shell
```

The browser setup opens automatically on first launch if no token is configured.
If a browser cannot open, use the local URL printed in your terminal or run:

```sh
karyo login --terminal
```

## Credentials

Previously installed as `ai-harness`? Run the installer above to install `karyo`,
then optionally run `uv tool uninstall ai-harness`. Your previously saved token
is still recognized. `karyo logout` removes both the current and legacy token files.

The setup page runs only on `127.0.0.1`, closes after a successful submission,
and expires after five minutes. Tokens are sent to Hugging Face to validate them;
Karyo has no hosted token collection service. The saved token lives in
`~/.config/karyo/token` (or `$XDG_CONFIG_HOME/karyo/token`) with owner-only
file permissions. This file is plaintext, not an encrypted keychain.

`HF_TOKEN` from the environment takes precedence, followed by a `.env` in the
current working directory, followed by the saved token. Tokens are not included
in the installed package. Token validation confirms the account credential;
provider permission, model availability, and billing are checked when inference runs.

```sh
karyo login     # Replace the saved token through the browser
karyo logout    # Delete the saved token (does not unset HF_TOKEN or edit .env)
```

## Update or uninstall

```sh
uv tool upgrade karyo
uv tool uninstall karyo
```

Run `karyo logout` before uninstalling to remove the saved credential.
Install [ripgrep](https://github.com/BurntSushi/ripgrep#installation) for the search
tool (`brew install ripgrep` on macOS or `sudo apt install ripgrep` on Ubuntu/WSL).
Other tools work without it.

## Development

Python 3.10+ is supported. The installer selects Python 3.13.

```sh
uv sync --locked
uv run karyo
uv run python -m unittest -v test_tools test_auth
uv build
```

The CLI operates in the directory where you launch it. Conversation memory lasts
for the current session. Model/provider settings are currently defined in
`cli.py` and `inference.py`; `config.json` does not configure the CLI.
