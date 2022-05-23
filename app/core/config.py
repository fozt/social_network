from pydantic import BaseSettings


class Settings(BaseSettings):
    instagram_login: str
    instagram_password: str
    tg_token: str
    sqlite_file_name = "database.sqlite"
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    class Config:
        env_file = ".env"


settings = Settings()
