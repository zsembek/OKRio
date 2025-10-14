import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure a minimal set of settings is available during tests so optional imports succeed.
os.environ.setdefault("BACKEND_URL", "http://localhost:8070")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")
os.environ.setdefault("ADMIN_EMAIL", "admin@example.com")
os.environ.setdefault("POSTGRES_URL", "postgresql+psycopg2://okrio:okrio@localhost:5439/okrio")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("AZURE_TENANT_ID", "00000000-0000-0000-0000-000000000000")
os.environ.setdefault("AZURE_CLIENT_ID", "00000000-0000-0000-0000-000000000000")
os.environ.setdefault("AZURE_REDIRECT_URI_FRONTEND", "http://localhost:5173/auth/callback")
os.environ.setdefault("AZURE_LOGOUT_REDIRECT_URI", "http://localhost:5173/logout")
os.environ.setdefault("AZURE_OAUTH_SCOPES", "openid profile email offline_access")
os.environ.setdefault("AZURE_AUTHORITY", "https://login.microsoftonline.com/common")
os.environ.setdefault("MS_GRAPH_BASE_URL", "https://graph.microsoft.com/v1.0")
os.environ.setdefault("MS_GRAPH_SCOPES", "User.Read")
