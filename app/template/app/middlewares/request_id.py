from fastapi import FastAPI
from asgi_correlation_id import CorrelationIdMiddleware


def add_request_id_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CorrelationIdMiddleware,
    )
