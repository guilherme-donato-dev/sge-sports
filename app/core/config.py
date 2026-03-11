from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "SGE Sports Store"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str

    # GEMINI    
    GOOGLE_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Stock Alerts
    LOW_STOCK_THRESHOLD: int = 10


settings = Settings()
