# todos/auth.py
import datetime
import jwt
from django.conf import settings
from django.contrib.auth.models import User
from ninja.security import HttpBearer, django_auth

HARDCODED_USERNAME = "admin"
HARDCODED_PASSWORD = "secret123"


def create_jwt_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2),
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            username = payload.get("sub")
            if username == HARDCODED_USERNAME:
                # Ensure a corresponding Django User object exists for request.auth / django_auth compatibility
                user, _ = User.objects.get_or_create(username=username)
                return user
        except jwt.PyJWTError:
            return None
        return None


jwt_auth = JWTAuth()
# Allows either a Bearer JWT token OR a standard Django session cookie
combined_auth = [jwt_auth, django_auth]
