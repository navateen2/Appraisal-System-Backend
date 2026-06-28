from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from middleware import configure_middleware
from auth.router import router as auth_router
from config import settings
from exceptions.handler import register_exception_handler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await
    yield


app = FastAPI(
    title="Appraisal App", description="Performance Appraisal Management System", version="1.0.0", lifespan=lifespan
)

configure_middleware(app)
register_exception_handler(app)
app.include_router(auth_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "message": f"Performance Appraisal Management System : {settings.app_env}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.0", port=8000, reload=True)
