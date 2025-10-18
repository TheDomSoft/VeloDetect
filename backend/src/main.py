import os
import uvicorn
from fastapi import FastAPI

from routers.minio_router import MinioRouter
from core.prisma import prisma
from core.config import settings

app = FastAPI()

app.include_router(MinioRouter().router)

@app.get("/")
async def root():
    return {"message": "Hello"}


@app.on_event("startup")
async def on_startup() -> None:
    # Ensure Prisma sees DATABASE_URL from our settings if not already set in the env
    if settings.DATABASE_URL:
        os.environ.setdefault("DATABASE_URL", settings.DATABASE_URL)
    await prisma.connect()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await prisma.disconnect()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)