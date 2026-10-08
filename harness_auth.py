"""Local browser onboarding. Credentials never pass through a hosted app."""
import getpass
import json
import os
import secrets
import ssl
import sys
import tempfile
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from html import escape
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs
from urllib.request import Request, urlopen
import certifi


class LoginError(ValueError):
    """A safe, user-facing authentication error without credential details."""


def token_path(app="karyo"):
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / app / "token"


def read_token():
    token = os.environ.get("HF_TOKEN", "").strip()
    if token:
        return token
    try:
        return token_path().read_text().strip() or None
    except FileNotFoundError:
        try:
            return token_path("ai-harness").read_text().strip() or None
        except FileNotFoundError:
            return None


def logout():
    for app in ("karyo", "ai-harness"):
        token_path(app).unlink(missing_ok=True)


def save_token(token):
    path = token_path()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(token)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def validate_token(token):
    if not token.startswith("hf_") or any(c.isspace() for c in token):
        raise LoginError("Enter a Hugging Face user access token starting with hf_.")
    request = Request("https://huggingface.co/api/whoami-v2", headers={"Authorization": "Bearer " + token})
    try:
        context = ssl.create_default_context(cafile=certifi.where())
        with urlopen(request, timeout=15, context=context) as response:
            json.load(response)
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise LoginError("Hugging Face rejected this token. Check that it is valid and has not been revoked.") from None
        raise LoginError("Hugging Face is temporarily unavailable. Please retry shortly.") from None
    except (URLError, OSError):
        raise LoginError("Could not connect securely to Hugging Face. Check your connection or proxy settings and retry.") from None
    except ValueError:
        raise LoginError("Hugging Face returned an unexpected response. Please retry shortly.") from None


def login(terminal=False):
    if terminal:
        if not sys.stdin.isatty():
            raise ValueError("Run login in a terminal, or set HF_TOKEN in your environment.")
        token = getpass.getpass("Hugging Face token (hidden): ").strip()
        validate_token(token)
        save_token(token)
        print("Token saved on this computer.")
        return token
    secret = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(32)
    result = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, body):
            data = body.encode()
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(data)

        def allowed(self):
            return self.headers.get("Host") == address and self.path == "/" + secret

        def do_GET(self):
            if not self.allowed():
                return self.reply(404, "Not found")
            self.reply(200, '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Connect Karyo</title>
<style>body{background:#111827;color:#eee;font:17px system-ui;margin:8vh auto;padding:24px;max-width:520px}h1{font-size:36px}p{line-height:1.6;color:#cbd5e1}a{color:#93c5fd}input,button{box-sizing:border-box;width:100%;padding:15px;border-radius:9px;margin:12px 0;font:inherit}button{background:#a3e635;border:0;cursor:pointer}small{color:#aab4c3}</style>
<h1>Connect Karyo</h1><p>Use your Hugging Face account to start coding.</p>
<p><a href="https://huggingface.co/settings/tokens" target="_blank" rel="noreferrer">Create a Hugging Face token ↗</a><br>Enable <strong>Make calls to Inference Providers</strong>.</p>
<form method="post"><input type="hidden" name="csrf" value="CSRF_VALUE"><label for="token">Hugging Face token</label><input id="token" name="token" type="password" placeholder="hf_…" autocomplete="off" required maxlength="512"><button>Save token and continue</button></form>
<small>Your token is validated with Hugging Face and stored in a private file on this computer. Inference usage is billed to your Hugging Face account.</small></html>'''.replace("CSRF_VALUE", csrf))

        def do_POST(self):
            # Privacy policies may suppress Origin on a legitimate form POST.
            # The independent form nonce remains required in every case.
            if not self.allowed() or self.headers.get("Origin") not in (None, "null", "http://" + address):
                return self.reply(403, "Request rejected")
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 2048:
                    return self.reply(400, "Invalid request size")
                fields = parse_qs(self.rfile.read(length).decode(), max_num_fields=2)
                if not secrets.compare_digest(fields.get("csrf", [""])[0].encode(), csrf.encode()):
                    return self.reply(403, "Request rejected. Reopen the setup page and try again.")
                token = fields.get("token", [""])[0].strip()
                validate_token(token)
            except LoginError as exc:
                return self.reply(400, escape(str(exc)) + '<p><a href="">Return to setup</a></p>')
            except (ValueError, OSError):
                return self.reply(400, 'Invalid form submission. <a href="">Return to setup</a>')
            try:
                save_token(token)
            except OSError:
                return self.reply(500, 'Cannot write the local token file. Check permissions on your Karyo config directory. <a href="">Retry</a>')
            result.append(token)
            self.reply(200, "<h1>You're connected.</h1><p>Close this tab and return to your terminal.</p>")

        def setup(self):
            super().setup()
            self.connection.settimeout(20)

    with HTTPServer(("127.0.0.1", 0), Handler) as server:
        address = "127.0.0.1:" + str(server.server_port)
        url = "http://" + address + "/" + secret
        print("Open this local setup page: " + url)
        print("Waiting up to 5 minutes. Ctrl+C cancels; use karyo login --terminal without a browser.")
        webbrowser.open(url)
        server.timeout = 1
        deadline = time.monotonic() + 300
        while not result and time.monotonic() < deadline:
            server.handle_request()
    if not result:
        raise ValueError("Login timed out. Run karyo login to try again.")
    print("Token saved on this computer.")
    return result[0]
