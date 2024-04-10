from sqlmodel import SQLModel, create_engine
from sqlalchemy.engine import URL
from .config import settings

url_object = URL.create(
    "postgresql",
    username=f"{settings.database_username}",
    password=f"{settings.database_password.get_secret_value()}",
    host=f"{settings.database_hostname}",
    port=f"{settings.database_port}",
    database=f"{settings.database_name}",
)

engine = create_engine(url_object, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
