import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
    
    DATABASE_ENGINE = os.getenv('DATABASE_ENGINE')
    DATABASE_NAME = os.getenv('DATABASE_NAME')
    
    CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
