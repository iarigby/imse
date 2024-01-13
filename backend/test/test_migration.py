import random

import pytest

from backend import schemas, generate
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
        sql_service.buy_ticket(user.id, random.choice(events).id)
        sql_service.buy_ticket(user.id, random.choice(events).id)

        tickets: list[schemas.Ticket] = sql_db.get_tickets()
        user_tickets = [ticket for ticket in tickets if ticket.user_id == user.id]
    migrate()
    mongo_db = MongoDatabase(mongo_client)
    migrated_users = mongo_db.get_users()
    migrated_events = mongo_db.get_events()
    migrated_venues = mongo_db.get_venues()
    migrated_tickets = mongo_db.get_tickets()
    migrated_user = mongo_db.get_user(user.id)
    migrated_user_tickets = [ticket for ticket in tickets if ticket.user_id == migrated_user.id]
    assert len(migrated_user_tickets) != 0
    assert(sorted(ticket.id for ticket in user_tickets) == sorted(ticket.id for ticket in migrated_user_tickets))
    assert len(users) == len(migrated_users)
    assert len(venues) == len(migrated_venues)
    assert len(events) == len(migrated_events)
    assert len(tickets) == len(migrated_tickets)
    assert sorted(user.id for user in users) == sorted(user.id for user in migrated_users)
