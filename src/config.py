"""Application configuration objects."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR.parent / 'instance'
INSTANCE_DIR.mkdir(exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = True
    DATABASE_PATH = os.environ.get('DATABASE_PATH', str(INSTANCE_DIR / 'campus_hub.db'))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', str((BASE_DIR / 'static' / 'images' / 'uploads')))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EMAIL_DOMAINS = None  # set to list like {'iu.edu'} if needed

class TestConfig(Config):
    TESTING = True
    DATABASE_PATH = os.environ.get('TEST_DATABASE_PATH', str(INSTANCE_DIR / 'test.db'))
    WTF_CSRF_ENABLED = False
