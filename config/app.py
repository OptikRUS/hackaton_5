from fastapi import FastAPI


def fastapi_app() -> FastAPI:
    from config.initializers import (
        init_app,
        init_routers,
        init_cors,
        init_database,
    )

    application: FastAPI = init_app()

    init_routers(application)
    init_cors(application)
    init_database(application)
    return application
