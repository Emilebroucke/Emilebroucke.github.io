import os
from dataclasses import dataclass


@dataclass
class Settings:
    data_dir: str = os.environ.get("DATA_DIR", os.path.abspath("./backend/data"))
    llm_provider: str = os.environ.get("LLM_PROVIDER", "openai")
    llm_base_url: str = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
    llm_api_key: str = os.environ.get("LLM_API_KEY", "")
    llm_model: str = os.environ.get("LLM_MODEL", "gpt-4o-mini")
    llm_temperature: float = float(os.environ.get("LLM_TEMPERATURE", "0.2"))
    llm_max_tokens: int = int(os.environ.get("LLM_MAX_TOKENS", "512"))
    embedding_model: str = os.environ.get(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    max_upload_mb: int = int(os.environ.get("MAX_UPLOAD_MB", "200"))


settings = Settings()
