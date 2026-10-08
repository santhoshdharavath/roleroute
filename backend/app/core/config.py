from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./roleroute.db"
    cors_origins: str = "http://localhost:3000"
    demo_user_id: int = 1
    demo_user_name: str = "Alex Rivera"
    demo_user_email: str = "alex@roleroute.demo"
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def llm_configured(self) -> bool:
        provider = self.llm_provider.strip().lower()
        if provider == "gemini":
            return bool(self.gemini_api_key.strip())
        if provider == "openai":
            return bool(self.openai_api_key.strip())
        return False


@lru_cache
def get_settings() -> Settings:
    return Settings()
