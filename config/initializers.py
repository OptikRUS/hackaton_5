from fastapi import FastAPI

from config.settings import settings


def init_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP.TITLE,
        version=settings.APP.VERSION,
        summary=settings.APP.SUMMARY,
    )
    return app


def init_routers(application: FastAPI) -> None:
    from config.routers import get_routers

    for router in get_routers():
        application.include_router(router)


def init_cors(application: FastAPI) -> None:
    from fastapi.middleware.cors import CORSMiddleware

    application.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "Authorization"],
        allow_origins=["*"],
    )
