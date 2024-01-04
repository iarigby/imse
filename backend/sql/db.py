from __future__ import annotations

import os
from contextlib import contextmanager

from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session

import backend.database
from backend.sql import models
from backend import schemas

SQLALCHEMY_DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL", "postgresql://postgres:postgres@localhost/backend")


def tickets_to_schema(tickets: list[models.Ticket]) -> list[schemas.Ticket]:
    return [schemas.Ticket(id=ticket.id, **ticket.__dict__) for ticket in tickets]


class SqlDatabase(backend.database.Database):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def database(engine):
        # noinspection PyPep8Naming
        return sessionmaker(autocommit=False, autoflush=True, bind=engine)

    @staticmethod
    def engine(conn_url=SQLALCHEMY_DATABASE_URL):
        if conn_url.startswith("sqlite://"):
            return create_engine(conn_url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
        else:
            return create_engine(conn_url)

    # noinspection PyPep8Naming
    @staticmethod
    @contextmanager
    def session(SessionMaker) -> SqlDatabase:
        session = SessionMaker()
        try:
            yield SqlDatabase(session)
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def reset(engine):
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)

    def get_user(self, user_id: str) -> schemas.User:
        user = self.db.query(models.User).filter_by(_id=user_id).one_or_none()
        return schemas.User(id=user.id, **user.__dict__)

    def get_users(self) -> list[schemas.User]:
        return [schemas.User(id=user.id, **user.__dict__) for user in self.db.query(models.User).all()]

    def add_user(self, user: schemas.NewUser):
        self.db.add(models.User(**user.model_dump()))
        self.db.commit()

    def add_ticket(self, ticket: schemas.NewTicket):
        self.db.add(models.Ticket(**ticket.model_dump()))
        self.db.commit()

    def get_event(self, event_id: str):
        event = self.db.query(models.Event).filter_by(_id=event_id).one_or_none()
        return schemas.Event(id=event.id, **event.__dict__)

    def decrease_user_balance(self, user_id: str, amount: int):
        self.db.query(models.User).filter_by(_id=user_id).update(
            {models.User.balance: models.User.balance - amount})
        self.db.commit()

    def add_venue(self, venue: schemas.NewVenue):
        self.db.add(models.Venue(**venue.model_dump()))
        self.db.commit()

    def get_venue(self, venue_id: str):
        venue = self.db.query(models.Venue).filter_by(_id=venue_id).one_or_none()
        return schemas.Venue(id=venue.id, **venue.__dict__)

    def get_venues(self):
        return [schemas.Venue(id=venue.id, **venue.__dict__) for venue in
                self.db.query(models.Venue).all()]

    def get_events_with_tickets(self) -> list[schemas.EventWithTickets]:  # type: ignore
        return [schemas.EventWithTickets(
            id=event.id,
            name=event.name,
            tickets=tickets_to_schema(event.tickets),
            price=event.price,
            venue_id=event.venue_id,

        )
            for event in self.db.query(models.Event).join(models.Ticket, isouter=True).all()]

    def get_event_with_tickets(self, event_id: str) -> schemas.EventWithTickets:
        event = self.db.query(models.Event
                              ).filter_by(_id=event_id).join(models.Ticket, isouter=True
                                                             ).one_or_none()
        return schemas.EventWithTickets(
            id=event.id,
            name=event.name,
            tickets=tickets_to_schema(event.tickets),
            price=event.price,
            venue_id=event.venue_id
        )

    def add_event(self, event: schemas.NewEvent):
        self.db.add(models.Event(**event.model_dump()))
        self.db.commit()

    def get_tickets(self) -> list[schemas.Ticket]:
        # noinspection PyTypeChecker
        return tickets_to_schema(self.db.query(models.Ticket).all())

    def get_events(self) -> list[schemas.Event]:
        return [schemas.Event(id=event.id, **event.__dict__)
                for event in self.db.query(models.Event).all()]
