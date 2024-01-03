import datetime
import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict


class NewUser(BaseModel):
    name: str
    balance: int = 0

    model_config = ConfigDict(from_attributes=True)


class User(NewUser):
    id: uuid.UUID


class TicketStatus(Enum):
    BOOKED = 0
    CANCELLED = 1


class NewTicket(BaseModel):
    purchase_date: datetime.datetime
    status: TicketStatus
    user_id: uuid.UUID
    event_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class Ticket(NewTicket):
    id: uuid.UUID


class NewEvent(BaseModel):
    name: str
    price: int = 0
    venue_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class Event(NewEvent):
    id: uuid.UUID


class EventWithTickets(Event):
    tickets: list[Ticket]


class NewVenue(BaseModel):
    name: str
    city: str
    capacity: int


class Venue(NewVenue):
    id: uuid.UUID
