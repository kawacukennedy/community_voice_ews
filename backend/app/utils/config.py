import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Community Voice EWS"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = "sqlite:///./ews.db"

    secret_key: str = "change-me-in-production"
    allowed_origins: str = "*"

    sms_provider: str = "africas_talking"
    sms_api_key: str = ""
    sms_username: str = "sandbox"
    sms_sender_id: str = ""

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    icpac_api_base: str = "https://maps.icpac.net/ogc"
    icpac_api_key: str = ""

    log_level: str = "INFO"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
