import pytest

from backend import schemas, generate
from backend.nosql.db import MongoDatabase


mongo_client = MongoDatabase.database()
db = MongoDatabase(mongo_client)


@pytest.mark.integration
def test_mongodb():
    MongoDatabase.reset(mongo_client)
    user = generate.user()
    db.add_user(user)
    users = db.get_users()
    assert users[0].first_name == user.first_name
