from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URI: str
    GOOGLE_MAPS_API_KEY: str
    allowed_origins: str
    API_BASE_URL: str  # 이 줄을 추가합니다

    class Config:
        env_file = "./.env"
        extra = "ignore"  # 이 줄을 추가합니다


settings = Settings()
settings.allowed_origins = settings.allowed_origins.split(',')