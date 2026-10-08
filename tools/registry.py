from tools.file_operations import list_files
from tools.file_operations import read_file
from tools.file_operations import write_file
from tools.shell import run_shell
from tools.search import search_files

TOOL_REGISTRY = {
    "search_files": {
        "handler": search_files,
        "schema": {
            "type": "function",
            "function": {
                "name": "search_files",
                "description": "Search text recursively with ripgrep. Returns file paths, line numbers, and matching lines. Respects ignore files, skips binary files, and defaults to skipping hidden files. Any accessible directory is allowed. Output is capped at 20 KB with a 15-second timeout.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Regular expression to search for"},
                        "path": {"type": "string", "description": "Search directory or file; defaults to current directory"},
                        "glob": {"type": ["string", "null"], "description": "Optional filename filter, e.g. *.py"},
                        "hidden": {"type": "boolean"},
                    },
                    "required": ["pattern"],
                    "additionalProperties": False,
                },
            },
        },
    },
    "run_shell": {
        "handler": run_shell,
        "schema": {
            "type": "function",
            "function": {
                "name": "run_shell",
                "description": "Execute a command with /bin/sh. Return stdout, stderr, exit code, and timeout status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"},
                        "cwd": {"type": ["string", "null"]},
                        "timeout_seconds": {"type": "number", "exclusiveMinimum": 0},
                    },
                    "required": ["command"],
                    "additionalProperties": False,
                },
            },
        },
    },
    "write_file": {
        "handler": write_file,
        "schema": {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write a UTF-8 file at any writable path. Relative paths use the current directory. Set overwrite=true to replace contents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                        "overwrite": {"type": "boolean"},
                    },
                    "required": ["path", "content"],
                    "additionalProperties": False,
                },
            },
        },
    },
    "read_file": {
        "handler": read_file,
        "schema": {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "read file content given path of file",
                "parameters": {
                    "type": "object",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"}
                        }
                    }
                }
            }
        }

    },
    "list_files": {
        "handler": list_files,
        "schema": {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List immediate workspace entries, optionally filtered by a filename glob.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "pattern": {"type": ["string", "null"]},
                    },
                    "additionalProperties": False,
                },
            },
        },
    },
}


def get_tool_schemas():
    return [tool["schema"] for tool in TOOL_REGISTRY.values()]
