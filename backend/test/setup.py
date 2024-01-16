import os

from sqlalchemy_utils import database_exists, create_database

from backend.sql import models
from backend.sql.db import SqlDatabase

db_url = os.environ.get('SQLALCHEMY_TEST_DATABASE_URL', "sqlite:///./test.db")
engine = SqlDatabase.engine(conn_url=db_url)
SessionMaker = SqlDatabase.database(engine)

try:
    if not database_exists(engine.url):
        create_database(engine.url)
    models.Base.metadata.create_all(engine)
except:
    pass

