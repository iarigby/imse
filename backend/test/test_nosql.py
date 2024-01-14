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


@pytest.mark.integration
def test_add_ticket():
    MongoDatabase.reset(mongo_client)
    user = db.add_user(generate.user())
    venue = db.add_venue(generate.venue())
    event = db.add_event(generate.event(venue.id))
    ticket = db.add_ticket(generate.ticket(user.id, event.id))
    event2 = db.get_event(event.id)
    assert event2.tickets[0].id == ticket.id
