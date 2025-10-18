from fastapi import APIRouter, Body, Path
from minio import Minio
from fastapi import Depends, HTTPException

from core.minio_client import get_minio_client
from services.minio_service import MinioService


class MinioRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/json", tags=["JSON Storage"])
        self.router.add_api_route("/upload/{filename}", self.upload_json, methods=["POST"])

    async def upload_json(
        self,
        filename: str = Path(..., description="The name of the file to upload"),
        data: dict = Body(..., description="The data to upload"),
        client: Minio = Depends(get_minio_client),
        minio_service: MinioService = Depends(MinioService)
    ):
        """Upload JSON file to MinIO"""
        try:
            return await minio_service.upload_json(filename, data, client)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))