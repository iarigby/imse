import random

import pytest

from backend import schemas, generate
from backend.database import OrderBy
from backend.nosql.db import MongoDatabase
from backend.services import EventService
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
        sql_service = EventService(sql_db)
        populate_database(sql_db)
        user = sql_db.add_user(generate.user(balance=200))
        users = sql_db.get_users()

        venues = sql_db.get_venues()
        events = sql_db.get_events()
        artists = sql_db.get_artists()
        sql_service.buy_ticket(user.id, random.choice(events).id)
        sql_service.buy_ticket(user.id, random.choice(events).id)

        tickets: list[schemas.Ticket] = sql_db.get_tickets()
        user_tickets = sql_db.get_tickets_for_user(user.id)
        venue_for_report = random.choice(venues).id
        report = sql_db.get_top_users_for_venue(venue_for_report, order_by=OrderBy.Ascending)
    migrate()
    mongo_db = MongoDatabase(mongo_client)
    migrated_users = mongo_db.get_users()
    migrated_events = mongo_db.get_events()
    migrated_venues = mongo_db.get_venues()
    migrated_tickets = mongo_db.get_tickets()
    migrated_artists = mongo_db.get_artists()
    migrated_user = mongo_db.get_user(user.id)
    migrated_user_tickets = mongo_db.get_tickets_for_user(migrated_user.id)
    migrated_report = mongo_db.get_top_users_for_venue(venue_for_report, order_by=OrderBy.Ascending)

    assert ([(str(r.user.id), r.tickets_purchased) for r in sorted(report, key=lambda r: r.user.id)] ==
            [(str(r.user.id), r.tickets_purchased) for r in sorted(migrated_report, key=lambda r: r.user.id)])

    assert len(migrated_user_tickets) != 0
    assert (sorted(user_ticket.ticket.id for user_ticket in user_tickets) == sorted(
        user_ticket.ticket.id for user_ticket in migrated_user_tickets))
    assert len(users) == len(migrated_users)
    assert len(venues) == len(migrated_venues)
    assert len(events) == len(migrated_events)
    assert len(tickets) == len(migrated_tickets)
    assert len(artists) == len(migrated_artists)

    assert sorted(user.id for user in users) == sorted(user.id for user in migrated_users)

    def sort_by_id(li):
        return sorted([e for e in li], key=lambda e: e.id)

    assert ([len(a.events) for a in sort_by_id(artists)] ==
            [len(a.events) for a in sort_by_id(migrated_artists)])
