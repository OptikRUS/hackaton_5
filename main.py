import uvicorn

from config.settings import settings
from config.app import fastapi_app


def run_service() -> None:
    uvicorn.run(
        fastapi_app(),
        host=settings.SITE.HOST,
        port=settings.SITE.PORT,
        loop=settings.SITE.LOOP,
        log_level=settings.SITE.LOG_LEVEL,
        reload_delay=settings.SITE.RELOAD_DELAY,
        access_log=settings.SITE.ACCESS_LOG,
    )


if __name__ == "__main__":
    run_service()
