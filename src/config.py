import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def env(name: str, default: str | None = None, required: bool = False) -> str | None:
    val = os.getenv(name, default)
    if required and not val:
        raise RuntimeError(f"Missing required env: {name}")
    return val


def _require(name: str) -> str:
    v = env(name, required=True)
    assert v is not None  # for pyright
    return v


class Settings:
    def __init__(self):
        self.model_key: str = _require("MODEL_PROVIDER_KEY")
        self.model_provider: str = _require("MODEL_PROVIDER").rstrip("/")
        self.model_name: str = _require("MODEL_NAME")
        self.smtp_host: str = _require("SMTP_HOST")
        self.smtp_port: int = int(env("SMTP_PORT", "587") or "587")
        self.smtp_user: str = _require("SMTP_USER")
        self.smtp_password: str = _require("SMTP_PASSWORD")
        self.smtp_from: str = _require("SMTP_FROM")

    def load_recipients(self) -> list[str]:
        from .subscribers import load_subscribers

        return load_subscribers("subscribers.csv")

    def __repr__(self) -> str:
        return f"Settings(model={self.model_name}, provider={self.model_provider})"
