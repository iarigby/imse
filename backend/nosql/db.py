from pymongo.mongo_client import MongoClient
import os

import backend.database
from backend import schemas


class MongoDatabase(backend.database.Database):
    def __init__(self):
        uri = os.environ.get('MONGO_URL', "mongodb://mongodb:27017/admin")
        self.client = MongoClient(uri)
        self.client.admin.command('ping')
        self.db = self.client.imse

    def reset(self):
        self.client.drop_database('imse')

    def get_user(self) -> schemas.User:
        pass

    def get_users(self) -> list[schemas.User]:
        users = self.db.users.find()
        return [schemas.User(id=user['_id'], **user) for user in users]

    def add_user(self, user: schemas.NewUser):
        self.db.users.insert_one(user.model_dump())

    def add_ticket(self, ticket: schemas.NewTicket):
        pass

    def get_events_with_tickets(self) -> list[schemas.EventWithTickets]:
        pass

    def add_event(self, event: schemas.NewEvent):
        pass
