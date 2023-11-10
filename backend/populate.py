from backend import schemas
from backend.database import Database


def populate_database(db: Database):
    db.add_user(schemas.NewUser(name="hello"))
