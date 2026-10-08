import json

from tools.registry import TOOL_REGISTRY


def dispatch_tool(name, arguments):
    try:
        handler = TOOL_REGISTRY[name]["handler"]
        return handler(**json.loads(arguments))
    except Exception as exc:
        return {"ok": False, "error": {"code": type(exc).__name__}}


def dispatch_tool_call(call):
    result = dispatch_tool(call.function.name, call.function.arguments)
    return {
        "role": "tool",
        "tool_call_id": call.id,
        "content": json.dumps(result),
    }
