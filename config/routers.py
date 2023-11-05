from fastapi import APIRouter


def get_routers() -> list[APIRouter]:
    from src.utd.api import video_router

    routers: list[APIRouter] = list()

    routers.append(video_router)

    return routers
