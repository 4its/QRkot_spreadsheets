# app/main.py

from fastapi import FastAPI

# Импортируем роутер.
from app.api.routers import main_router
from app.core.config import settings
from app.core.init_db import create_first_superuser

app = FastAPI(title=settings.app_title)

# Подключаем роутер.
app.include_router(main_router)


@app.on_event('startup')
async def startup():
    await create_first_superuser()
