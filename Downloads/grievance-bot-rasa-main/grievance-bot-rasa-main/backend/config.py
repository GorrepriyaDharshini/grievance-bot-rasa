"""Application configuration for ResolveX Flask backend."""
import os

SECRET_KEY = os.environ.get("RESOLVEX_SECRET_KEY", "dev-change-me-college-project")
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
