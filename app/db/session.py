from sqlmodel import SQLModel, create_engine
from sqlmodel.sql.expression import SelectOfScalar

from app.core.config import settings

engine = create_engine(
    f"postgresql://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
)

SelectOfScalar.inherit_cache = True


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
