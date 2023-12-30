import sqlalchemy.exc
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

import backend.database
from backend.sql import models
from backend import schemas


# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@postgres_server/backend"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost/backend"


class SqlDatabase(backend.database.Database):
    def __init__(self, conn_url=SQLALCHEMY_DATABASE_URL, engine=None):
        if engine is None:
            if conn_url.startswith("sqlite://"):
                engine = create_engine(conn_url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
            else:
                engine = create_engine(conn_url)
        self.engine = engine
        # noinspection PyPep8Naming
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def reset(self):
        try:
            models.Base.metadata.drop_all(bind=self.engine)
        except sqlalchemy.exc.OperationalError:
            pass
        models.Base.metadata.create_all(bind=self.engine)

    def get_users(self) -> list[schemas.User]:
        session = self.SessionLocal()
        with session.begin():
            res = session.query(models.User).all()
            users = [schemas.User(id=user.id, name=user.name) for user in res]
        session.close()
        return users

    def add_user(self, user: schemas.NewUser):
        session = self.SessionLocal()
        session.add(models.User(**user.model_dump()))
        session.commit()
        session.close()
