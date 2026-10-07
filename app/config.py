# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    model_dir: str = "models/rubert_base_v1"    


settings = Settings()