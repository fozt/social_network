from typing import Optional, Union

from pydantic import BaseSettings


class Settings(BaseSettings):
    INSTAGRAM_LOGIN: str
    INSTAGRAM_PASSWORD: str
    TG_TOKEN: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: Union[int, str]
    DATABASE_NAME: str
    BASE_URL: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
