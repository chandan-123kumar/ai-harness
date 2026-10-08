#!/bin/sh
# Install AI Harness on macOS or Linux without cloning the repository.
set -eu
case "$(uname -s)" in
  Darwin|Linux) ;;
  *) echo 'Use macOS, Linux, or Windows with WSL.' >&2; exit 1 ;;
esac
if ! command -v uv >/dev/null 2>&1; then
  echo 'Installing uv…'
  installer=$(mktemp)
  trap 'rm -f "$installer"' EXIT HUP INT TERM
  curl -fsSL https://astral.sh/uv/install.sh -o "$installer"
  sh "$installer"
  export PATH="$HOME/.local/bin:$PATH"
fi
uv tool install --python 3.13 --from 'https://github.com/chandan-123kumar/ai-harness/archive/refs/heads/main.zip' ai-harness
uv tool update-shell
bin_dir=$(uv tool dir --bin)
echo 'AI Harness installed. Connecting your Hugging Face account…'
"$bin_dir/ai-harness" login
echo 'Open a new terminal, enter your project folder, and run: ai-harness'
