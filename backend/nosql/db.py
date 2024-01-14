from __future__ import annotations

import os
from contextlib import contextmanager

from bson import ObjectId
from pymongo.mongo_client import MongoClient

import backend.database
from backend import schemas


def to_object_id(item_id: str | ObjectId):
    if type(item_id) == str:
        return ObjectId(item_id)
    return item_id


class MongoDatabase(backend.database.Database):
    @staticmethod
    @contextmanager
    def session(client: MongoClient) -> MongoDatabase:
        yield MongoDatabase(client)

    @staticmethod
    def database(args=None) -> MongoClient:
        uri = f'mongodb://{os.environ.get("MONGO_HOST", "localhost")}:27017/admin?uuidRepresentation=standard'
        client = MongoClient(uri, uuidRepresentation='standard')
        client.admin.command('ping')
        return client

    def __init__(self, client: MongoClient):
        self.client = client

    @staticmethod
    def reset(client):
        client.drop_database('imse')

    def get_user(self, user_id: str) -> schemas.User:
        user = self.client.imse.users.find_one({'_id': user_id})
        return schemas.User.model_validate(user)

    def get_users(self) -> list[schemas.User]:
        users = self.client.imse.users.find()
        return [schemas.User.model_validate(user) for user in users]

    def add_user(self, user: schemas.NewUser) -> schemas.User:
        user_id = self.client.imse.users.insert_one(user.model_dump(by_alias=True)).inserted_id
        return schemas.User.model_validate(self.get_user(user_id))

    def add_artist(self, artist: schemas.NewArtist):
        pass

    def get_artist(self, artist_id: str) -> schemas.Artist:
        pass

    def get_artists(self):
        pass

    def get_events(self):
        return [schemas.Event.model_validate(event) for event in self.client.imse.events.find()]

    def get_top_users_for_venue(self, venue_id) -> list[schemas.VenueReport]:
        pass

    def get_user_by_email(self, user_name: str) -> schemas.User:
        pass

    def add_ticket(self, ticket: schemas.NewTicket):
        pass
        self.client.imse.events.update_one({
            '_id': to_object_id(ticket.event_id)},
            {'$push': {'tickets': ticket.model_dump(by_alias=True)}
             })

    def get_ticket(self, ticket_id: str) -> schemas.Ticket:
        pass

    def del_ticket(self, ticket: schemas.Ticket.id):
        pass

    def get_tickets(self) -> list[schemas.Ticket]:
        return [schemas.Ticket.model_validate(ticket) for ticket in self.client.imse.tickets.find()]

    def get_event(self, event_id: str):
        event = self.client.imse.events.find_one({'_id': to_object_id(event_id)})
        return schemas.Event.model_validate(event)

    def decrease_user_balance(self, user_id: str, amount: int):
        pass

    def get_events_with_tickets(self) -> list[schemas.Event]:
        pass

    def get_event_with_tickets(self, ticket_id: str) -> schemas.Event:
        pass

    def add_event(self, event: schemas.NewEvent):
        event_id = self.client.imse.events.insert_one(event.model_dump(by_alias=True)).inserted_id
        return schemas.Event.model_validate(self.get_event(event_id))

    def add_venue(self, venue: schemas.NewVenue):
        venue_id = self.client.imse.venues.insert_one(venue.model_dump(by_alias=True)).inserted_id
        return schemas.Venue.model_validate(self.get_venue(venue_id))

    def get_venue(self, venue_id: str):
        venue = self.client.imse.venues.find_one({'_id': venue_id})
        return schemas.Venue.model_validate(venue)

    def get_venues(self):
        return [schemas.Venue.model_validate(venue) for venue in self.client.imse.venues.find()]

    def add_users(self, users: list[schemas.User]):
        self.client.imse.users.insert_many([user.model_dump(by_alias=True) for user in users])

    def add_venues(self, venues: list[schemas.Venue]):
        self.client.imse.venues.insert_many([venue.model_dump(by_alias=True) for venue in venues])

    def add_events(self, events: list[schemas.Event]):
        self.client.imse.events.insert_many([event.model_dump(by_alias=True) for event in events])

    def add_tickets(self, tickets: list[schemas.Ticket]):
        self.client.imse.tickets.insert_many([ticket.model_dump(by_alias=True) for ticket in tickets])
