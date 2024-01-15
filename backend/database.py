from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum

from backend import schemas


class OrderBy(Enum):
    Descending = -1
    Ascending = 1


class Database(ABC):
    @staticmethod
    @abstractmethod
    @contextmanager
    def session(args) -> Database:
        pass

    @staticmethod
    @abstractmethod
    def database(args):
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> schemas.User:
        pass

    @abstractmethod
    def get_user_by_email(self, user_name: str) -> schemas.User:
        pass

    @abstractmethod
    def get_users(self) -> list[schemas.User]:
        pass

    @abstractmethod
    def add_user(self, user: schemas.NewUser) -> schemas.User:
        pass

    @abstractmethod
    def add_artist(self, artist: schemas.NewArtist):
        pass

    @abstractmethod
    def get_artist(self, artist_id: str) -> schemas.Artist:
        pass

    @abstractmethod
    def get_artists(self):
        pass

    @abstractmethod
    def add_ticket(self, ticket: schemas.NewTicket):
        pass

    @abstractmethod
    def return_ticket(self, user_id: str, event_id: str):
        pass

    @abstractmethod
    def get_ticket(self, user_id: str, event_id: str) -> schemas.Ticket:
        pass

    @abstractmethod
    def get_tickets(self) -> list[schemas.Ticket]:
        pass

    @abstractmethod
    def get_event(self, event_id: str) -> schemas.Event:
        pass

    @abstractmethod
    def get_events_by_artist(self, artist_id: str) -> list[schemas.Event]:
        pass

    @abstractmethod
    def get_events(self):
        pass

    @abstractmethod
    def decrease_user_balance(self, user_id: str, amount: int):
        pass

    @abstractmethod
    def increase_user_balance(self, user_id: str, amount: int):
        pass

    @abstractmethod
    def add_event(self, event: schemas.NewEvent) -> schemas.Event:
        pass

    @abstractmethod
    def add_venue(self, venue: schemas.NewVenue) -> schemas.Venue:
        pass

    @abstractmethod
    def get_venue(self, venue_id: str):
        pass

    @abstractmethod
    def get_venues(self):
        pass

    @abstractmethod
    def get_tickets_for_user(self, user_id) -> list[schemas.UserTicket]:
        pass

    @abstractmethod
    def get_top_users_for_venue(self, venue_id: str, order_by: OrderBy) -> list[schemas.VenueReport]:
        pass

    @abstractmethod
    def get_artist_success(self, venue_id) -> list[schemas.ArtistSuccess]:
        pass

    @staticmethod
    @abstractmethod
    def reset(client):
        pass
