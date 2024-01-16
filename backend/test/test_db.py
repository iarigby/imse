import contextlib
from typing import ContextManager, Callable

from backend import generate, services, schemas, database
from backend.database import OrderBy
import pytest

from .setup import SessionMaker
from ..nosql.db import MongoDatabase
from ..sql.db import SqlDatabase


def with_sql() -> ContextManager[SqlDatabase]:
    @contextlib.contextmanager
    def wrapped():
        with SqlDatabase.session(SessionMaker) as db:
            yield db
    return wrapped()


def with_mongo() -> ContextManager[MongoDatabase]:
    @contextlib.contextmanager
    def wrapped():
        mongo_client = MongoDatabase.database()
        yield MongoDatabase(mongo_client)
    return wrapped()


@pytest.mark.parametrize(
    "db_session",
    [with_sql,
     pytest.param(with_mongo, marks=pytest.mark.integration)])
def test_add_user(db_session):
    with db_session() as db:
        new_user = generate.user()
        db.add_user(new_user)
        users = db.get_users()
        assert users[0].id is not None
        assert users[0].first_name == new_user.first_name


@pytest.mark.parametrize(
    "db_session",
    [with_sql,
     pytest.param(with_mongo, marks=pytest.mark.integration)])
def test_add_get_artist(db_session):
    with db_session() as db:
        venue = db.add_venue(generate.venue())
        event = db.add_event(generate.event(venue.id))
        artist = db.add_artist(generate.artist())
        assert artist == db.get_artist(artist.id)
        db.add_artist_to_event(artist.id, event.id)
        assert db.get_artist(artist.id).events == [event.id]
        assert db.get_event(event.id).artists == [artist.id]


@pytest.mark.parametrize(
    "db_session",
    [with_sql,
     pytest.param(with_mongo, marks=pytest.mark.integration)])
def test_buy_ticket(db_session):
    with db_session() as db:
        service = services.EventService(db)
        db.add_venue(generate.venue())
        db.add_user(generate.user(balance=20))
        venues = db.get_venues()
        db.add_event(generate.event(venues[0].id, price=10))
        users = db.get_users()
        user_id = users[0].id
        events = db.get_events()
        service.buy_ticket(user_id, events[0].id)

    with db_session() as db:
        events = db.get_events()
        user = db.get_user(user_id)
        assert len(events) == 1
        assert len(events[0].tickets) == 1
        assert user.balance == 10


@pytest.mark.parametrize(
    "db_session",
    [pytest.param(with_sql, marks=pytest.mark.integration),
     pytest.param(with_mongo, marks=pytest.mark.integration)])
def test_get_top_users_for_venue(db_session: Callable[[], ContextManager[database.Database]]):
    with db_session() as db:
        service = services.EventService(db)
        user1 = db.add_user(generate.user(balance=1000))
        user2 = db.add_user(generate.user(balance=1000))
        user3 = db.add_user(generate.user())
        venue1 = db.add_venue(generate.venue())
        venue2 = db.add_venue(generate.venue())
        event1 = db.add_event(generate.event(venue1.id))
        event2 = db.add_event(generate.event(venue1.id))
        event3 = db.add_event(generate.event(venue2.id))
        service.buy_ticket(user1.id, event1.id)
        service.buy_ticket(user1.id, event2.id)
        service.buy_ticket(user2.id, event1.id)
        service.buy_ticket(user2.id, event3.id)
        reports1 = db.get_top_users_for_venue(venue1.id, OrderBy.Ascending)
        reports1_desc = db.get_top_users_for_venue(venue1.id, OrderBy.Descending)

        reports2 = db.get_top_users_for_venue(venue2.id, OrderBy.Ascending)
        assert len(reports1) == 2
        assert len(reports2) == 1

    assert reports1 == sorted(reports1, key=lambda r: r.tickets_purchased)
    assert reports1_desc == sorted(reports1_desc, key=lambda r: r.tickets_purchased, reverse=True)

    def find_user(reports, user_id) -> schemas.VenueReport:
        return next(report for report in reports if report.user.id == user_id)

    assert find_user(reports1, user1.id).tickets_purchased == 2

    assert find_user(reports1, user2.id).tickets_purchased == 1
    assert find_user(reports2, user2.id).tickets_purchased == 1

    with pytest.raises(StopIteration):
        find_user(reports1, user3.id)

    with pytest.raises(StopIteration):
        find_user(reports2, user2)
