import uuid
from abc import ABC, abstractmethod

from backend import schemas


class Database(ABC):
    @abstractmethod
    def get_user(self, user_id: uuid.UUID) -> schemas.User:
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
    def get_event(self, event_id: uuid.UUID):
        pass

    @abstractmethod
    def decrease_user_balance(self, user_id: uuid.UUID, amount: int):
        pass

    @abstractmethod
    def get_events_with_tickets(self) -> list[schemas.EventWithTickets]:
        pass

    @abstractmethod
    def get_event_with_tickets(self, ticket_id: uuid.UUID) -> schemas.EventWithTickets:
        pass

    @abstractmethod
    def add_event(self, event: schemas.NewEvent):
        pass

    @abstractmethod
    def add_venue(self, venue: schemas.NewVenue):
        pass

    @abstractmethod
    def get_venue(self, venue_id: uuid.UUID):
        pass

    @abstractmethod
    def get_venues(self):
        pass

    @abstractmethod
    def reset(self):
        pass
