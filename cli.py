from dataclasses import asdict

from inference import create_client
from memory.memory import Memory
from tools.registry import get_tool_schemas
from tools.dispatcher import dispatch_tool_call


MAX_TOOL_ROUNDS = 1


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


if __name__ == "__main__":
    memory = Memory()
    client = create_client()
    while True:
        main(input(">> "), memory, client)
