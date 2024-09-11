from pydantic import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'QRKot'
    app_description: str = 'Приложение QRKot.'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SUNICORN'

    class Config:
        env_file = '.env'


settings = Settings()
