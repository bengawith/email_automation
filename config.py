import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from var.env
env_path = str(next(Path.cwd().rglob('.env'), None))
load_dotenv(env_path)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "my-very-secret-key")
    SESSION_TYPE = 'filesystem'
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = True
    
    # MSAL / OAuth settings
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    TENANT_ID = os.getenv("TENANT_ID")
    REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:5000/authorized")
    MSAL_SCOPE = ["Mail.Send"]
    SIGNATURE_TEXT = os.getenv("SIGNATURE_TEXT")
