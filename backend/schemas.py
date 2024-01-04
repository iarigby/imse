import datetime
import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, AfterValidator, BeforeValidator
from typing_extensions import Annotated
from bson import ObjectId as _ObjectId


def check_object_id(value):
    if _ObjectId.is_valid(value):
        return str(value)
    return value


ObjectId = Annotated[uuid.UUID | str, BeforeValidator(check_object_id)]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class NewUser(ORMModel):
    name: str
    balance: int = 0


class User(NewUser):
    id: ObjectId = Field(alias='_id')


class TicketStatus(Enum):
    BOOKED = 0
    CANCELLED = 1


class NewTicket(ORMModel):
    purchase_date: datetime.datetime
    status: TicketStatus
    user_id: str | uuid.UUID
    event_id: str | uuid.UUID


class Ticket(NewTicket):
    id: str | uuid.UUID = Field(alias='_id')


class NewArtist(ORMModel):
    name: str


class Artist(NewArtist):
    id: str | uuid.UUID = Field(alias='_id')


class NewEvent(ORMModel):
    name: str
    price: int = 0
    venue_id: str | uuid.UUID
    date: datetime.datetime
    artists: list[Artist]


class Event(NewEvent):
    id: str | uuid.UUID = Field(alias='_id')


class EventWithTickets(Event):
    tickets: list[Ticket]


class NewVenue(ORMModel):
    name: str
    city: str
    capacity: int


class Venue(NewVenue):
    id: str | uuid.UUID = Field(alias='_id')
