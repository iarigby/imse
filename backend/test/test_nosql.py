import pytest

from backend import schemas
from backend.nosql.db import MongoDatabase


@pytest.mark.integration
def test_mongodb():
    db = MongoDatabase()
    db.reset()
    db.add_user(schemas.User(name="username"))
    users = db.get_users()
    assert users[0].name == "username"
