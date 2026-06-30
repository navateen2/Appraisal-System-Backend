from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from middleware.context import set_current_user_id, reset_current_user_id
from config import settings

SECRET_KEY = settings.jwt_secret
ALGORITHM = settings.jwt_algorithm


class AuditContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_id = None
        authorization: str = request.headers.get("Authorization", "")

        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                # Adjust key string if your payload sets it as "sub" or another identifier
                user_id = payload.get("id")
            except JWTError:
                pass

        token_ctx = set_current_user_id(user_id)
        try:
            response = await call_next(request)
            return response
        finally:
            reset_current_user_id(token_ctx)
