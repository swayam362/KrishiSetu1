import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "krushisetu_super_secret_dev_key_2026")
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    
    # MongoDB Config (Supports MONGO_URI, MONGODB_URI)
    MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI") or "mongodb://localhost:27017/krushisetu_db"
    DB_NAME = os.getenv("DB_NAME", "krushisetu_db")
    
    # JWT Authentication Config (Supports JWT_SECRET, JWT_SECRET_KEY)
    JWT_SECRET = os.getenv("JWT_SECRET") or os.getenv("JWT_SECRET_KEY") or "krushisetu_jwt_master_secret_key_prod_grade"
    JWT_ACCESS_TOKEN_EXPIRES_HOURS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 24))
    
    # Static & Frontend paths
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.getenv("UPLOAD_FOLDER", "uploads"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
