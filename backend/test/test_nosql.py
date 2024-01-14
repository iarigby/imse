import pytest

from backend import schemas, generate, services
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


@pytest.mark.integration
def test_get_top_users_for_venue():
    MongoDatabase.reset(mongo_client)
    service = services.EventService(db)
    user1 = db.add_user(generate.user(balance=1000))
    user2 = db.add_user(generate.user(balance=1000))
    user3 = db.add_user(generate.user())
    venue = db.add_venue(generate.venue())
    event1 = db.add_event(generate.event(venue.id))
    event2 = db.add_event(generate.event(venue.id))
    service.buy_ticket(user1.id, event1.id)
    service.buy_ticket(user1.id, event2.id)
    service.buy_ticket(user2.id, event1.id)
    reports = db.get_top_users_for_venue(venue.id)

    def find_user(user_id) -> schemas.VenueReport:
        return next(report for report in reports if report.user.id == user_id)

    assert find_user(user1.id).tickets_purchased == 2
    assert find_user(user2.id).tickets_purchased == 1

    with pytest.raises(StopIteration):
        find_user(user3.id)
