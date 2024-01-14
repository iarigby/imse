from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Type

from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session

import backend.database
from backend.sql import models
from backend import schemas

SQLALCHEMY_DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL", "postgresql://postgres:postgres@localhost/backend")


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
        return schemas.User.model_validate(user)

    def get_user_by_email(self, email: str) -> schemas.User:
        user = self.db.query(models.User).filter_by(email=email).one_or_none()
        return schemas.User.model_validate(user)

    def get_users(self) -> list[schemas.User]:
        return [schemas.User.model_validate(user) for user in self.db.query(models.User).all()]

    def add_user(self, user: schemas.NewUser) -> schemas.User:
        db_user = models.User(**user.model_dump())
        self.db.add(db_user)
        self.db.commit()
        return schemas.User.model_validate(db_user)

    def decrease_user_balance(self, user_id: str, amount: int):
        self.db.query(models.User).filter_by(_id=user_id).update(
            {models.User.balance: models.User.balance - amount})
        self.db.commit()

    def add_venue(self, venue: schemas.NewVenue) -> schemas.Venue:
        db_venue = models.Venue(**venue.model_dump())
        self.db.add(db_venue)
        self.db.commit()
        return schemas.Venue.model_validate(db_venue)

    def get_venue(self, venue_id: str):
        venue = self.db.query(models.Venue).filter_by(_id=venue_id).one_or_none()
        return schemas.Venue.model_validate(venue)

    def get_venues(self):
        return [schemas.Venue.model_validate(venue) for venue in
                self.db.query(models.Venue).all()]

    def get_events(self) -> list[schemas.EventWithTickets]:  # type: ignore
        events = (self.db.query(models.Event)
                  .join(models.Ticket, isouter=True)
                  .join(models.EventArtist, isouter=True)
                  .join(models.Artist, isouter=True)
                  .all())
        return [schemas.Event.model_validate(event) for event in events]

    def get_event(self, event_id: str) -> schemas.Event:
        event = (self.db.query(models.Event)
                 .filter_by(_id=event_id)
                 .join(models.Ticket, isouter=True)
                 .join(models.EventArtist, isouter=True)
                 .join(models.Artist, isouter=True)
                 .one_or_none())
        return schemas.Event.model_validate(event)

    def add_event(self, event: schemas.NewEvent) -> schemas.Event:
        db_event = models.Event(**event.model_dump())
        self.db.add(db_event)
        self.db.commit()
        return schemas.Event.model_validate(db_event)

    def add_artist(self, artist: schemas.NewArtist):
        self.db.add(models.Ticket(**artist.model_dump()))
        self.db.commit()

    def get_artists(self) -> list[schemas.Artist]:
        return [schemas.Artist.model_validate(t) for t in self.db.query(models.Ticket).all()]

    def get_artist(self, artist_id: str) -> schemas.Artist:
        artist = (self.db.query(models.Artist)
                  .filter_by(_id=artist_id)
                  .join(models.Venue, isouter=True)
                  .join(models.Ticket, isouter=True)
                  .one_or_none())
        return schemas.Artist.model_validate(artist)

    def add_ticket(self, ticket: schemas.NewTicket):
        self.db.add(models.Ticket(**ticket.model_dump()))
        self.db.commit()

    def get_tickets(self) -> list[schemas.Ticket]:
        return [schemas.Ticket.model_validate(t) for t in self.db.query(models.Ticket).all()]

    def get_ticket(self, user_id: str, event_id: str) -> schemas.Ticket | None:
        ticket = (self.db.query(models.Ticket)
                  .filter_by(user_id=user_id, event_id=event_id)
                  .join(models.Event, isouter=True)
                  .join(models.User, isouter=True)
                  .one_or_none())
        if not ticket:
            return ticket
        return schemas.Ticket.model_validate(ticket)

    def del_ticket(self, ticket_id):
        ticket = (self.db.query(models.Ticket)
                  .filter_by(_id=ticket_id)
                  .join(models.User, isouter=True)
                  .join(models.Event, isouter=True)
                  .one_or_none())
        self.db.delete(ticket)
        self.db.commit()
        return

    # need to add date
    def get_top_users_for_venue(self, venue_id) -> list[schemas.VenueReport]:
        users: list[Type[models.User]] = (self.db.query(models.User)
                                          .join(models.Ticket)
                                          .join(models.Event)
                                          .filter_by(venue_id=venue_id)
                                          .all())
        return [schemas.VenueReport(user=schemas.User.model_validate(user),
                                    tickets_purchased=len(user.tickets)
                                    ) for user in users]
