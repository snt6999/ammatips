import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Telugu Amma Tips API"
    jwt_secret: str = "replace-this-with-a-long-random-secret"
    jwt_expire_minutes: int = 720
    admin_email: str = "admin@teluguammatips.in"
    admin_password: str = "ChangeMe123!"
    cors_origins: str = "http://localhost:5173"
    database_url: str = "sqlite:///./telugu_amma_tips.db"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    @property
    def cors_origin_list(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
