from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus
import os
import logging
from dotenv import load_dotenv

# Configure logger
logger = logging.getLogger(__name__)

# Check if .env file exists and load it
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
if not os.path.exists(env_path):
    logger.error(f".env file not found at {env_path}. Please create one with required environment variables.")
    raise FileNotFoundError(f".env file not found at {env_path}")

load_dotenv(env_path)


class Settings(BaseSettings):
    # Application
    PORT: int = int(os.getenv("PORT", 5000))

    # Database
    DB_NAME: str = os.getenv("DB_NAME", "kosix_db")
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "admin@kosix123")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 6061))

    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", 7))
    
    # Cloudinary Settings
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET_KEY", "")

    @property
    def DATABASE_URL(self) -> str:
        # URL-encode password to handle special characters like @
        encoded_password = quote_plus(self.DB_PASSWORD)
        return f"postgresql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
