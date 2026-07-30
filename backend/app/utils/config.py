import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Community Voice EWS"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = ""
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_jwt_secret: str = ""

    secret_key: str = "change-me-in-production"
    allowed_origins: str = "http://localhost:8000,http://localhost:5500,https://*.vercel.app"

    sms_provider: str = "africas_talking"
    sms_api_key: str = ""
    sms_username: str = "sandbox"
    sms_sender_id: str = ""

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    icpac_api_base: str = "https://maps.icpac.net/ogc"
    icpac_api_key: str = ""

    mapbox_token: str = ""
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
