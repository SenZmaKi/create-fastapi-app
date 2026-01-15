from fastapi_docshield import DocShield
from app.utils.settings import settings
from fastapi import FastAPI


def add_docshield_middleware(app: FastAPI) -> None:
    if settings.deployment_environment != "production":
        return
    DocShield(
        app=app,
        credentials={settings.docs_admin_username: settings.docs_admin_password},
    )
