import cv2
import torch
from config.settings import base_dir, settings
from fastapi import APIRouter, File, UploadFile, WebSocket, status
from minio import Minio
from ultralytics import YOLO

from src.utd.models import Files
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
    file_path = f"src/uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    saved_video = await Files.create(filename=file.filename, path=file_path)
    return {"filename": saved_video.filename, "path": saved_video.path}


@router.get(
    "", status_code=status.HTTP_200_OK, response_model=list[UploadResponse],
)
async def get_videos():
    return await Files.all()


@router.websocket("")
async def websocket_video_endpoint(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_json()
    rtsp_url = data.get("rtsp_url")
    yolo_model = set_model()
    cap = cv2.VideoCapture(rtsp_url)
    while cap.isOpened() and websocket.application_state == websocket.application_state.CONNECTED:
        while True:
            ret, frame = cap.read()
            if not ret and websocket.application_state == websocket.application_state.CONNECTED:
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
