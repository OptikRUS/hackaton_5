from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    path: str
