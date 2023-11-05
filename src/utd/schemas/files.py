from pydantic import BaseModel


class UploadResponse(BaseModel):
    bucket_name: str
    object_name: str
    etag: str
