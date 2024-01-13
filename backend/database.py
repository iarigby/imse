from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager

from backend import schemas


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
    def add_ticket(self, ticket: schemas.NewTicket):
        pass

    @abstractmethod
    def del_ticket(self, ticket: schemas.Ticket.id):
        pass

    @abstractmethod
    def get_ticket(self, ticket_id: str) -> schemas.Ticket:
        pass

    @abstractmethod
    def get_tickets(self):
        pass

    @abstractmethod
    def get_event(self, event_id: str) -> schemas.Event:
        pass

    @abstractmethod
    def get_events(self):
        pass

    @abstractmethod
    def decrease_user_balance(self, user_id: str, amount: int):
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
    def get_top_users_for_venue(self, venue_id) -> list[schemas.VenueReport]:
        pass

    @staticmethod
    @abstractmethod
    def reset(client):
        pass
