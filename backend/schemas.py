import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, BeforeValidator
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
    first_name: str
    last_name: str
    email: str
    password: str
    role: str
    profile_visibility: str
    balance: int = 0


class User(NewUser):
    id: ObjectId = Field(alias='_id')


class VenueReport(BaseModel):
    user: User
    tickets_purchased: int


class NewTicket(ORMModel):
    purchase_date: datetime.datetime
    status: str
    user_id: str | uuid.UUID
    event_id: str | uuid.UUID


class Ticket(NewTicket):
    id: ObjectId = Field(alias='_id')


class NewArtist(ORMModel):
    first_name: str
    last_name: str
    stage_name: str


class Artist(NewArtist):
    id: ObjectId = Field(alias='_id')


class NewEvent(ORMModel):
    name: str
    price: int = 0
    venue_id: str | uuid.UUID
    date: datetime.datetime
    artists: list[Artist]
    tickets: list[Ticket]


class Event(NewEvent):
    id: ObjectId = Field(alias='_id')


class NewVenue(ORMModel):
    name: str
    city: str
    capacity: int


class Venue(NewVenue):
    id: ObjectId = Field(alias='_id')
