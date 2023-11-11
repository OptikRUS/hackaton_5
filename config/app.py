from fastapi import FastAPI


def fastapi_app() -> FastAPI:
    from config.initializers import (
        init_app,
        init_routers,
        init_cors,
    )

    application: FastAPI = init_app()

    init_routers(application)
    init_cors(application)
    return application
