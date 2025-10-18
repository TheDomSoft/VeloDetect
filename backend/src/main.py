import uvicorn
from fastapi import FastAPI

from routers.minio_router import MinioRouter

app = FastAPI()

app.include_router(MinioRouter().router)

@app.get("/")
async def root():
    return {"message": "Hello"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)