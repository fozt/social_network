from sqlmodel import SQLModel, create_engine

from app import db
from app.core.config import settings

engine = create_engine(settings.sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
