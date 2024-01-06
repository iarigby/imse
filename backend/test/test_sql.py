import pytest

from backend import generate, schemas
from backend.sql.db import SqlDatabase
from backend import services

engine = SqlDatabase.engine(conn_url="sqlite:///./test.db")
SessionMaker = SqlDatabase.database(engine)


def test_sqldb():
    SqlDatabase.reset(engine)
    with SqlDatabase.session(SessionMaker) as db:
        new_user = generate.user()
        db.add_user(new_user)
        users = db.get_users()
        assert users[0].id is not None
        assert users[0].first_name == new_user.first_name


# Untested: user cannot buy ticket twice
def test_buy_ticket():
    SqlDatabase.reset(engine)
    with SqlDatabase.session(SessionMaker) as db:
        service = services.EventService(db)
        db.add_venue(generate.venue())
        db.add_user(generate.user(balance=20))
        venues = db.get_venues()
        db.add_event(generate.event(venues[0].id, price=10))
        users = db.get_users()
        user_id = users[0].id
        events = db.get_events()
        service.buy_ticket(user_id, events[0].id)

    with SqlDatabase.session(SessionMaker) as db:
        events = db.get_events()
        user = db.get_user(user_id)
        assert len(events) == 1
        assert len(events[0].tickets) == 1
        assert user.balance == 10


def test_get_top_users_for_venue():
    SqlDatabase.reset(engine)
    with SqlDatabase.session(SessionMaker) as db:
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
