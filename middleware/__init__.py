from middleware.logger import RequestLoggingMiddleware
from middleware.auditor import AuditContextMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI


def configure_middleware(app: FastAPI) -> None:
    """
    Register ASGI middleware. Last added is outermost (runs first on the request path).

    Stack (request): CORS -> request logging -> auditor -> routes.
    """
    app.add_middleware(AuditContextMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time"],
    )
