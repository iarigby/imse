from __future__ import annotations

import os
import uuid
from contextlib import contextmanager

from sqlalchemy import create_engine, StaticPool, func, text, distinct
from sqlalchemy.orm import sessionmaker, Session

import backend.database
from backend.database import OrderBy
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

    def increase_user_balance(self, user_id: str, amount: int):
        self.db.query(models.User).filter_by(_id=user_id).update(
            {models.User.balance: models.User.balance + amount}
        )
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

    def add_artist_to_event(self, artist_id: str, event_id: str) -> models.EventArtist:
        event_artist = models.EventArtist.insert().values(left_id=event_id, right_id=artist_id)
        self.db.execute(event_artist)
        self.db.commit()
        return event_artist

    def add_artist(self, artist: schemas.NewArtist) -> schemas.Artist:
        new_artist = models.Artist(**artist.model_dump())
        self.db.add(new_artist)
        self.db.commit()
        return schemas.Artist.model_validate(new_artist)

    def get_artists(self) -> list[schemas.Artist]:
        return [schemas.Artist.model_validate(t) for t in self.db.query(models.Artist).all()]

    def get_artist(self, artist_id: str) -> schemas.Artist:
        artist = (self.db.query(models.Artist)
                  .filter_by(_id=artist_id)
                  .join(models.EventArtist, isouter=True)
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

    def return_ticket(self, user_id, event_id):
        (self.db.query(models.Ticket)
         .filter_by(user_id=user_id, event_id=event_id).update({models.Ticket.status: "cancelled"}))
        self.db.commit()
        return

    def get_tickets_for_user(self, user_id) -> list[schemas.UserTicket]:
        tickets = self.db.query(models.Ticket).filter_by(user_id=user_id).join(models.Event).all()
        return [schemas.UserTicket(ticket=schemas.Ticket.model_validate(ticket),
                                   event=schemas.Event.model_validate(ticket.event)) for ticket in tickets]

    # need to add date
    def get_top_users_for_venue(self, venue_id, order_by: OrderBy) -> list[schemas.VenueReport]:
        order_by_mapping = {
            order_by.Ascending: 'ASC',
            order_by.Descending: 'DESC'
        }
        stmt = text(f"""select "user", count(*) from "user"
        join public.ticket t on "user"._id = t.user_id
        join public.event e on e._id = t.event_id
        join public.venue v on v._id = e.venue_id
                                where v._id = '{venue_id}'
        group by "user"._id
        order by count(*) {order_by_mapping[order_by]}
                """)

        users_with_counts = self.db.execute(stmt)

        def query_result_to_user(user_csv, ticket_count) -> schemas.VenueReport:
            user_fields = user_csv.replace('(', '').replace(')', '').split(',')
            user = schemas.User(
                _id=uuid.UUID(user_fields[0]),
                first_name=user_fields[1],
                last_name=user_fields[2],
                email=user_fields[3],
                password=user_fields[4],
                role=user_fields[5],
                profile_visibility=user_fields[6],
                balance=int(user_fields[7])
            )
            return schemas.VenueReport(user=user, tickets_purchased=ticket_count)
        return [query_result_to_user(user, tickets_purchased) for user, tickets_purchased in users_with_counts]

    def get_artist_info(self, artist_id: str) -> schemas.ArtistReport:
        # Joining Artist, EventArtist, Event, and Ticket tables
        query = self.db.query(
            models.Artist.first_name.label('first_name'),
            func.count(distinct(models.Event._id)).label('number_of_events'),
            func.count(func.nullif(models.Ticket.status, 'cancelled')).label('number_of_booked_tickets'),
            func.count(func.nullif(models.Ticket.status, 'booked')).label('number_of_cancelled_tickets')
        ).join(
            models.EventArtist, models.Artist._id == models.EventArtist.c.right_id
        ).join(
            models.Event, models.EventArtist.c.left_id == models.Event._id
        ).join(
            models.Ticket, models.Ticket.event_id == models.Event._id
        ).filter(
            models.Artist._id == artist_id
        ).group_by(
            models.Artist.first_name
        )

        # Execute the query
        result = query.one_or_none()

        # Return the result
        return schemas.ArtistReport(artist_name=result.first_name,
                                    number_of_events=result.number_of_events,
                                    number_of_booked_tickets=result.number_of_booked_tickets,
                                    number_of_cancelled_tickets=result.number_of_cancelled_tickets
                                    )