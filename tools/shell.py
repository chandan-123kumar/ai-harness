import math
import os
import signal
import subprocess


def run_shell(command, cwd=None, timeout_seconds=30):
    """Execute a command using /bin/sh and capture its output."""
    if not isinstance(command, str) or not command.strip():
        raise ValueError("command must be a non-empty string")
    if cwd is not None and not isinstance(cwd, str):
        raise ValueError("cwd must be a string or null")
    if (isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(timeout_seconds) or timeout_seconds <= 0):
        raise ValueError("timeout_seconds must be positive and finite")

    with subprocess.Popen(
        command, shell=True, executable="/bin/sh", cwd=cwd,
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace", start_new_session=True,
    ) as process:
        timed_out = False
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = process.communicate()

    return {
        "ok": process.returncode == 0 and not timed_out,
        "exit_code": process.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "timed_out": timed_out,
    }
