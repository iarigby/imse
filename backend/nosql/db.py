from __future__ import annotations

import os
from contextlib import contextmanager

from pymongo.mongo_client import MongoClient

import backend.database
from backend import schemas


class MongoDatabase(backend.database.Database):
    @staticmethod
    @contextmanager
    def session(client: MongoClient) -> MongoDatabase:
        yield MongoDatabase(client)

    @staticmethod
    def database(args=None):
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
        pass

    def get_users(self) -> list[schemas.User]:
        users = self.client.imse.users.find()
        return [schemas.User.model_validate(user) for user in users]

    def add_user(self, user: schemas.NewUser):
        self.client.imse.users.insert_one(user.model_dump())

    def add_ticket(self, ticket: schemas.NewTicket):
        pass

    def get_event(self, event_id: str):
        pass

    def decrease_user_balance(self, user_id: str, amount: int):
        pass

    def get_events_with_tickets(self) -> list[schemas.Event]:
        pass

    def get_event_with_tickets(self, ticket_id: str) -> schemas.Event:
        pass

    def add_event(self, event: schemas.NewEvent):
        pass

    def add_venue(self, venue: schemas.NewVenue):
        pass

    def get_venue(self, venue_id: str):
        pass

    def get_venues(self):
        pass
