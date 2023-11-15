from io import BytesIO

import cv2
import torch
from config.settings import base_dir, settings
from fastapi import APIRouter, File, UploadFile, WebSocket, status
from minio import Minio
from starlette.responses import HTMLResponse, StreamingResponse
from ultralytics import YOLO

from src.utd.schemas.files import UploadResponse

router: APIRouter = APIRouter(prefix="/video", tags=["video"])

client = Minio(
    endpoint=f"{settings.S3.HOST}:{settings.S3.PORT}",
    access_key=settings.S3.USER,
    secret_key=settings.S3.PASSWORD,
    secure=False,
)


def set_model():
    model = YOLO(base_dir + "/best.pt")
    device = torch.device("cpu")
    model.to(device)
    return model


@router.post(
    "/upload", status_code=status.HTTP_201_CREATED, response_model=UploadResponse,
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
    "/{name}", response_class=HTMLResponse, status_code=status.HTTP_206_PARTIAL_CONTENT,
)
async def stream_video(name: str) -> StreamingResponse:
    bucket_object = client.get_object(bucket_name="videos", object_name=name)
    return StreamingResponse(
        BytesIO(bucket_object.read()),
        headers=bucket_object.headers,
        media_type="video/mp4",
        status_code=status.HTTP_206_PARTIAL_CONTENT,
    )


@router.websocket("")
async def websocket_video_endpoint(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_json()
    if data.get("is_closed"):
        await websocket.close()
    rtsp_url = data["rtsp_url"]
    yolo_model = set_model()
    cap = cv2.VideoCapture(rtsp_url)
    while cap.isOpened() and websocket.application_state == websocket.application_state.CONNECTED:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            resized_frame = cv2.resize(frame, (640, 640))
            results = yolo_model(resized_frame)
            if (len(results) > 0):
                print(results)
                for result in results:
                    boxes = result.boxes.xywh.cpu()
                    for idx in range(len(boxes)):
                        cur_id_box = int(result.boxes[idx].cls.item())
                        x, y, w, h = boxes[idx]
                        x_orig = int(x * frame.shape[1] / 640)
                        y_orig = int(y * frame.shape[0] / 640)
                        w_orig = int(w * frame.shape[1] / 640)
                        h_orig = int(h * frame.shape[0] / 640)
                        cv2.rectangle(frame, (int(x_orig - w_orig / 2), int(y_orig - h_orig / 2)),
                                      (int(x_orig + w_orig / 2), int(y_orig + h_orig / 2)), (0, 0, 255), 2)
                        cv2.putText(frame, str(result.names[cur_id_box]), (int(x_orig), int(y_orig)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                ret, buffer = cv2.imencode(".jpg", frame)
                frame = buffer.tobytes()
                await websocket.send_bytes(frame)
    cap.release()
    cv2.destroyAllWindows()
    await websocket.close()
