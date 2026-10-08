from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from harness_auth import read_token, login
from karyo_config import load_config


def error_details(exc):
    """Safe diagnostics: never include request headers, credentials or raw bodies."""
    status = getattr(getattr(exc, "response", None), "status_code", None)
    messages = {
        400: "The provider rejected the request. Check model settings and tool schemas.",
        401: "Authentication failed. Run karyo login and check HF_TOKEN overrides.",
        402: "Inference credits or billing are required on your Hugging Face account.",
        403: "Access denied. Check token inference permissions and model access.",
        404: "The model or endpoint was not found on this provider. Try --provider or --model.",
        429: "The provider rate limit was reached. Retry later.",
    }
    message = messages.get(status)
    if message is None:
        if isinstance(status, int) and status >= 500:
            message = "The inference service failed. Retry later."
        elif isinstance(exc, OSError):
            message = "A local file or network operation failed. Check permissions and connectivity."
        else:
            message = "Request failed. Check the error type and trace for the failing call."
    return {"type": type(exc).__name__, "http_status": status if isinstance(status, int) else None, "message": message}

def create_client(provider=None, timeout=None):
    if provider is None or timeout is None:
        config = load_config()
        provider = config['provider'] if provider is None else provider
        timeout = config['timeout_seconds'] if timeout is None else timeout
    load_dotenv(Path.cwd() / ".env", override=False)
    token = read_token()
    if not token:
        token = login()

    return InferenceClient(provider=provider, api_key=token, timeout=timeout)
