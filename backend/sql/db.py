import os
import uuid

import sqlalchemy.exc
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

import backend.database
from backend.sql import models
from backend import schemas

SQLALCHEMY_DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL", "postgresql://postgres:postgres@localhost/backend")


def tickets_to_schema(tickets: list[models.Ticket]) -> list[schemas.Ticket]:
    return [schemas.Ticket(id=ticket.id, **ticket.__dict__) for ticket in tickets]


class SqlDatabase(backend.database.Database):
    def __init__(self, conn_url=SQLALCHEMY_DATABASE_URL, engine=None):
        if engine is None:
            if conn_url.startswith("sqlite://"):
                engine = create_engine(conn_url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
            else:
                engine = create_engine(conn_url)
        self.engine = engine
        # noinspection PyPep8Naming
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=self.engine)

    def reset(self):
        try:
            models.Base.metadata.drop_all(bind=self.engine)
        except sqlalchemy.exc.OperationalError:
            pass
        models.Base.metadata.create_all(bind=self.engine)

    def get_user(self, user_id: uuid.UUID) -> schemas.User:
        with self.SessionLocal() as session:
            user = session.query(models.User).filter_by(_id=user_id).one_or_none()
            return schemas.User(id=user.id, **user.__dict__)

    def get_users(self) -> list[schemas.User]:
        with self.SessionLocal() as session:
            return [schemas.User(id=user.id, **user.__dict__) for user in session.query(models.User).all()]

    def add_user(self, user: schemas.NewUser):
        with self.SessionLocal() as session:
            session.add(models.User(**user.model_dump()))
            session.commit()

    def add_ticket(self, ticket: schemas.NewTicket):
        with self.SessionLocal() as session:
            session.add(models.Ticket(**ticket.model_dump()))
            session.commit()

    def get_event(self, event_id: uuid.UUID):
        with self.SessionLocal() as session:
            event = session.query(models.Event).filter_by(_id=event_id).one_or_none()
            return schemas.Event(id=event.id, **event.__dict__)

    def decrease_user_balance(self, user_id: uuid.UUID, amount: int):
        with self.SessionLocal() as session:
            session.query(models.User).filter_by(_id=user_id).update(
                {models.User.balance: models.User.balance - amount})
            session.commit()

    def add_venue(self, venue: schemas.NewVenue):
        with self.SessionLocal() as session:
            session.add(models.Venue(**venue.model_dump()))
            session.commit()

    def get_venue(self, venue_id: uuid.UUID):
        with self.SessionLocal() as session:
            venue = session.query(models.Venue).filter_by(_id=venue_id).one_or_none()
            return schemas.Venue(id=venue.id, **venue.__dict__)

    def get_venues(self):
        with self.SessionLocal() as session:
            return [schemas.Venue(id=venue.id, **venue.__dict__) for venue in
                    session.query(models.Venue).all()]

    def get_events_with_tickets(self) -> list[schemas.EventWithTickets]:  # type: ignore
        with self.SessionLocal() as session:
            return [schemas.EventWithTickets(
                id=event.id,
                name=event.name,
                tickets=tickets_to_schema(event.tickets),
                price=event.price,
                venue_id=event.venue_id,

            )
                for event in session.query(models.Event).join(models.Ticket, isouter=True).all()]

    def get_event_with_tickets(self, event_id: uuid.UUID) -> schemas.EventWithTickets:
        with self.SessionLocal() as session:
            event = session.query(models.Event
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
        with self.SessionLocal() as session:
            session.add(models.Event(**event.model_dump()))
            session.commit()

    def get_tickets(self) -> list[schemas.Ticket]:
        with self.SessionLocal() as session:
            # noinspection PyTypeChecker
            return tickets_to_schema(session.query(models.Ticket).all())

    def get_events(self) -> list[schemas.Event]:
        with self.SessionLocal() as session:
            return [schemas.Event(id=event.id, **event.__dict__)
                    for event in session.query(models.Event).all()]
