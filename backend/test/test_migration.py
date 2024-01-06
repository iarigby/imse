import pytest

from backend.nosql.db import MongoDatabase
from backend.sql.db import SqlDatabase
from backend.worker import migrate
from backend.populate import populate_database


@pytest.mark.integration
def test_migration():
    engine = SqlDatabase.engine()
    SessionMaker = SqlDatabase.database(engine)

    SqlDatabase.reset(engine)
    mongo_client = MongoDatabase.database()
    MongoDatabase.reset(mongo_client)
    with SqlDatabase.session(SessionMaker) as sql_db:
        populate_database(sql_db)
        users = sql_db.get_users()
        venues = sql_db.get_venues()
        events = sql_db.get_events()
    migrate()
    mongo_db = MongoDatabase(mongo_client)
    migrated_users = mongo_db.get_users()
    migrated_events = mongo_db.get_events()
    migrated_venues = mongo_db.get_venues()
    assert len(users) == len(migrated_users)
    assert len(venues) == len(migrated_venues)
    assert len(events) == len(migrated_events)
