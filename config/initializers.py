from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from config.settings import settings


def init_app() -> FastAPI:
    return FastAPI(
        title=settings.APP.TITLE,
        version=settings.APP.VERSION,
        summary=settings.APP.SUMMARY,
    )


def init_routers(application: FastAPI) -> None:
    from config.routers import get_routers

    for router in get_routers():
        application.include_router(router)


def init_database(application: FastAPI) -> None:
    register_tortoise(
        application,
        db_url="sqlite://:memory:",
        modules={"models": ["src.utd.models"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )


def init_cors(application: FastAPI) -> None:
    from fastapi.middleware.cors import CORSMiddleware

    application.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_origins=["*"],
    )
