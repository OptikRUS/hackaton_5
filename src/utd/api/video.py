from io import BytesIO

from fastapi import APIRouter, UploadFile, File, status
from starlette.responses import HTMLResponse, StreamingResponse
from minio import Minio

from config.settings import settings
from src.utd.schemas.files import UploadResponse

router: APIRouter = APIRouter(prefix="/video", tags=["video"])


client = Minio(
    endpoint=f"{settings.S3.HOST}:{settings.S3.PORT}",
    access_key=settings.S3.USER,
    secret_key=settings.S3.PASSWORD,
    secure=False,
)


@router.post(
    "/upload", status_code=status.HTTP_201_CREATED, response_model=UploadResponse
)
async def upload_video(file: UploadFile = File(...)):
    uploaded = client.put_object(
        bucket_name="videos",
        object_name=file.filename,
        data=file.file,
        content_type=file.content_type,
        length=file.size,
    )
    return UploadResponse(
        bucket_name=uploaded.bucket_name,
        object_name=uploaded.object_name,
        etag=uploaded.etag,
    )


@router.get(
    "/{name}", response_class=HTMLResponse, status_code=status.HTTP_206_PARTIAL_CONTENT
)
async def stream_video(name: str) -> StreamingResponse:
    bucket_object = client.get_object(bucket_name="videos", object_name=name)
    return StreamingResponse(
        BytesIO(bucket_object.read()),
        headers=bucket_object.headers,
        media_type="video/mp4",
        status_code=status.HTTP_206_PARTIAL_CONTENT,
    )
