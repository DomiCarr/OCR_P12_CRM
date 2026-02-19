# config/config.py
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()


class Config:
    """Configuration loader for environment variables."""
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SENTRY_DSN = os.getenv("SENTRY_DSN")

    @classmethod
    def get_db_url(cls):
        """Return formatted SQLAlchemy database URL."""
        return (
            f"mysql+mysqlconnector://{cls.DB_USER}:{cls.DB_PASSWORD}@"
            f"{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )