from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from harness_auth import read_token, login

def create_client(provider: str = "novita", timeout: float = 60):
    load_dotenv(Path.cwd() / ".env", override=False)
    token = read_token()
    if not token:
        token = login()

    return InferenceClient(provider=provider, api_key=token, timeout=timeout)
