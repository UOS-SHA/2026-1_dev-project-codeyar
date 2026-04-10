import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    USER_AGENTS: list[str] = ["CodeYar-Client/1.0", "CodeYar-Admin/1.0"]  # 클라이언트 User-Agent 필터링

    # Judge0 설정 (Cloud API 기준)
    JUDGE0_API_URL: str = "https://judge0-ce.p.rapidapi.com"
    JUDGE0_API_KEY: str = ""  # .env에서 읽어옴

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
