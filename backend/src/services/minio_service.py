from minio import Minio
from fastapi import Depends, HTTPException
from core.minio_client import get_minio_client
import json
import io
from core.config import settings
from datetime import datetime


class MinioService:
    def __init__(self):
        pass

    async def upload_json(
        self,
        filename: str,
        data: dict,
        client: Minio = Depends(get_minio_client)
    ):
        """Upload JSON file to MinIO"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            json_bytes = json.dumps(data).encode("utf-8")
            client.put_object(
                settings.MINIO_BUCKET,
                f"{filename}_{timestamp}.json",
                data=io.BytesIO(json_bytes),
                length=len(json_bytes),
                content_type="application/json"
            )
            return {"message": f"{filename}.json uploaded successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))