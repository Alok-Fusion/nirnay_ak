import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "NIRNAY AI Financial Decision Intelligence"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "nirnay_super_secret_key_change_me_in_production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # SQLite local DB file
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./nirnay.db")
    
    class Config:
        case_sensitive = True

settings = Settings()
