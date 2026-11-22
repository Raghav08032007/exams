"""
Application configuration.
Values are loaded from environment variables (see .env.example).
SQLAlchemy has been removed — database access is via raw PyMySQL.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration shared by all environments."""
    SECRET_KEY    = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-in-production")
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 52428800))  # 50 MB
    ALLOWED_EXTENSIONS = {"pdf"}
    # Raw DATABASE_URL parsed by app/db.py
    DATABASE_URL  = os.environ.get("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/examvault")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL must be set in production")


class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "mysql+pymysql://root:@localhost:3306/examvault_test")
    JWT_SECRET_KEY = "test-jwt-secret"


config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
    "default":     DevelopmentConfig,
}
