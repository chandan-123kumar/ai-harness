import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

def create_client(provider: str = "novita", timeout: float = 60):
    load_dotenv(Path(__file__).with_name(".env"), override=False)
    token = os.getenv("HF_TOKEN")
    if not token:
        raise ValueError("Set HF_TOKEN in .env or your environment before starting the CLI.")

    return InferenceClient(provider=provider, api_key=token, timeout=timeout)
