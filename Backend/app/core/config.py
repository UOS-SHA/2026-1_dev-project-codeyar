from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "" # .env에서 읽어옴

    JWT_SECRET: str = "" # .env에서 읽어옴

    JUDGE0_API_URL: str = "https://judge0-ce.p.rapidapi.com"
    JUDGE0_API_KEY: str = "" # .env에서 읽어옴
    JUDGE0_RAPIDAPI_HOST: str = "judge0-ce.p.rapidapi.com"
    JUDGE0_USE_RAPIDAPI: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
