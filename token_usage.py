"""Provider-reported token accounting, separate from model-visible tools."""
import json
import os
from dataclasses import asdict, is_dataclass
from types import SimpleNamespace
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


FIELDS = ("input_tokens", "output_tokens", "total_tokens")


def get_field(obj, name):
    return obj.get(name) if isinstance(obj, dict) else getattr(obj, name, None)


def count(value):
    return value if type(value) is int and value >= 0 else None


def snapshot(value):
    """Detach JSON-compatible SDK responses from mutable conversation state."""
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, SimpleNamespace):
        value = vars(value)
    if isinstance(value, dict):
        return {key: snapshot(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [snapshot(item) for item in value]
    return value


def trace_directory():
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "karyo" / "traces"


class TokenUsage:
    def __init__(self, trace_path=None, include_content=False):
        self.include_content = include_content
        self.session_id = str(uuid4())
        self.records = []
        self.turn = 0
        self.sequence = 0
        self.closed = False
        self.project = str(Path.cwd())
        self.trace_path = Path(trace_path).expanduser() if trace_path else (trace_directory() / (self.session_id + ".jsonl") if include_content else None)
        if self.trace_path:
            self.trace_path.parent.mkdir(parents=True, exist_ok=True)
            # Fail before inference if the requested trace cannot be opened.
            with os.fdopen(os.open(self.trace_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600), "a", encoding="utf-8"):
                pass

    def write_event(self, event):
        if self.trace_path:
            try:
                with self.trace_path.open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(event) + "\n")
            except OSError:
                print("Could not append trace; session counts remain available through /usage.", file=sys.stderr)

    def event(self, kind, **data):
        self.sequence += 1
        self.write_event({
            "session_id": self.session_id, "project": self.project,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": kind, "sequence": self.sequence, "turn": self.turn,
            **snapshot(data),
        })

    def begin_session(self):
        self.event("session_started", status="open")

    def end_session(self, status="closed"):
        if not self.closed:
            self.event("session_ended", status=status)
            self.closed = True

    def user_query(self, message):
        self.turn += 1
        if self.include_content:
            self.event("user_query", content=message)

    def start(self, request=None):
        event = {
            "session_id": self.session_id, "request": len(self.records) + 1,
            "project": self.project, "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "pending", "event": "started",
            "turn": self.turn,
        }
        if self.include_content:
            event["input"] = snapshot(request)
        self.write_event(event)

    def record(self, response=None, *, elapsed_ms=0, status="ok", request=None, error=None):
        usage = get_field(response, "usage")
        record = {
            "session_id": self.session_id,
            "request": len(self.records) + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "event": "finished",
            "turn": self.turn,
            "project": self.project,
            "elapsed_ms": round(elapsed_ms),
            "input_tokens": count(get_field(usage, "prompt_tokens")),
            "output_tokens": count(get_field(usage, "completion_tokens")),
            "total_tokens": count(get_field(usage, "total_tokens")),
        }
        if self.include_content:
            record["input"] = snapshot(request)
            record["output"] = snapshot(response)
        if error is not None:
            record["error"] = snapshot(error)
        self.records.append(record)
        self.write_event(record)
        numbers = [f"{record[field]:,}" if record[field] is not None else "unknown" for field in FIELDS]
        print(f"[tokens #{record['request']} · {status}] input {numbers[0]} | output {numbers[1]} | total {numbers[2]}", file=sys.stderr)
        return record

    def summary(self):
        parts = []
        for field, label in zip(FIELDS, ("input", "output", "total")):
            known = [record[field] for record in self.records if record[field] is not None]
            missing = len(self.records) - len(known)
            text = f"{label} {sum(known):,}" if known or not self.records else f"{label} unknown"
            if missing:
                text += f" ({missing} request(s) unreported)"
            parts.append(text)
        return f"Session: {len(self.records)} request(s) | " + " | ".join(parts)
