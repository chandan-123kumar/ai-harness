from dataclasses import asdict

from inference import create_client
from memory.memory import Memory
from tools.registry import get_tool_schemas
from tools.dispatcher import dispatch_tool_call


MAX_TOOL_ROUNDS = 10


def main(msg, memory, client=None):
    client = client if client is not None else create_client()
    memory.save_to_memory("user", msg)
    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model="Qwen/Qwen3-Coder-Next",
            messages=memory.get_memory(),
            tools=get_tool_schemas(),
        )
        message = response.choices[0].message
        print(message)
        saved = {"role": "assistant", "content": message.content}
        if message.tool_calls:
            saved["tool_calls"] = [asdict(call) for call in message.tool_calls]
        memory.save_message(saved)
        if not message.tool_calls:
            print(message.content or "[No text returned]")
            return
        for call in message.tool_calls:
            print(call)
            result = dispatch_tool_call(call)
            print(result)
            memory.save_message(result)
    print("Stopped after reaching the tool-round limit.")


def run():
    import argparse
    from harness_auth import login, logout, LoginError

    parser = argparse.ArgumentParser(description="Karyo — a terminal coding assistant")
    parser.add_argument("--version", action="version", version="karyo 0.2.1")
    commands = parser.add_subparsers(dest="command")
    auth = commands.add_parser("login", help="Connect your Hugging Face account")
    auth.add_argument("--terminal", action="store_true", help="Enter a hidden token in the terminal")
    commands.add_parser("logout", help="Remove the token saved by Karyo")
    args = parser.parse_args()
    try:
        if args.command == "login":
            login(terminal=args.terminal)
            return 0
        if args.command == "logout":
            logout()
            print("Saved token removed. HF_TOKEN environment variables and .env files are unchanged.")
            return 0
        memory = Memory()
        client = create_client()
        print("Karyo · Type /exit to quit.")
        print("This agent can write files and run shell commands with your user permissions.")
        while True:
            message = input(">> ").strip()
            if message in ("/exit", "/quit"):
                return 0
            if message:
                main(message, memory, client)
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")
        return 0
    except LoginError as exc:
        print(str(exc))
        return 1
    except Exception:
        print("Unable to complete the request. Check your connection, HF token and inference credits. Run karyo login to reconnect.")
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
