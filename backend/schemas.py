import datetime
import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, BeforeValidator, field_validator, model_validator
from typing_extensions import Annotated
from bson import ObjectId as _ObjectId

from backend.sql import models


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

class ArtistReport(BaseModel):
    artist_name: str
    number_of_events: int
    number_of_booked_tickets: int
    number_of_cancelled_tickets: int

class NewTicket(ORMModel):
    purchase_date: datetime.datetime
    status: str
    user_id: str | uuid.UUID
    event_id: str | uuid.UUID


class Ticket(NewTicket):
    id: ObjectId = Field(alias='_id')

    @model_validator(mode='before')
    def check_card_number_omitted(cls, data: Any) -> Any:
        if type(data) == models.Ticket:
            return data
        if '_id' not in data:
            for foreign_key in ['user_id', 'venue_id']:
                if foreign_key in data and type(data[foreign_key]) != str:
                    data[foreign_key] = str(data[foreign_key])
            data['_id'] = data['event_id'] + data['user_id']
        return data


class NewArtist(ORMModel):
    first_name: str
    last_name: str
    stage_name: str


class Artist(NewArtist):
    id: ObjectId = Field(alias='_id')


class ArtistSuccess(BaseModel):
    artist: Artist
    sold_tickets: int
    returned_tickets: int


class NewEvent(ORMModel):
    name: str
    price: int = 0
    venue_id: ObjectId
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


class UserTicket(BaseModel):
    ticket: Ticket
    event: Event
