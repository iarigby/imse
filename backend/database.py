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
    def get_users(self) -> list[schemas.User]:
        pass

    @abstractmethod
    def add_user(self, user: schemas.NewUser):
        pass

    @abstractmethod
    def add_ticket(self, ticket: schemas.NewTicket):
        pass

    @abstractmethod
    def get_event(self, event_id: str):
        pass

    @abstractmethod
    def decrease_user_balance(self, user_id: str, amount: int):
        pass

    @abstractmethod
    def add_event(self, event: schemas.NewEvent):
        pass

    @abstractmethod
    def add_venue(self, venue: schemas.NewVenue):
        pass

    @abstractmethod
    def get_venue(self, venue_id: str):
        pass

    @abstractmethod
    def get_venues(self):
        pass

    @staticmethod
    @abstractmethod
    def reset(client):
        pass
