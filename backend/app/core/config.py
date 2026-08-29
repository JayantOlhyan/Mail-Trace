import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "MailTrace Phase 1 Ingestion Engine"
    ENVIRONMENT: str = "development"
    MAX_EMAIL_SIZE_MB: int = 25
    EVIDENCE_STORAGE_PATH: str = os.path.join(os.getcwd(), "evidence_store")
    DATABASE_URL: str = "sqlite+aiosqlite:///./mailtrace.db"

    @property
    def max_bytes(self) -> int:
        return self.MAX_EMAIL_SIZE_MB * 1024 * 1024

settings = Settings()

os.makedirs(settings.EVIDENCE_STORAGE_PATH, exist_ok=True)
