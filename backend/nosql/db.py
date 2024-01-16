from __future__ import annotations

import os
import uuid
from contextlib import contextmanager
from typing import Dict, Any

import pymongo.collection
from bson import ObjectId
from pymongo.mongo_client import MongoClient

import backend.database
from backend.database import OrderBy
from backend import schemas


def to_object_id(item_id: str | ObjectId):
    if type(item_id) == str:
        if ObjectId.is_valid(item_id):
            return ObjectId(item_id)
        else:
            return uuid.UUID(item_id)
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
        user = self.users.find_one({'_id': to_object_id(user_id)})
        return schemas.User.model_validate(user)

    def get_users(self) -> list[schemas.User]:
        users = self.users.find()
        return [schemas.User.model_validate(user) for user in users]

    def add_user(self, user: schemas.NewUser) -> schemas.User:
        user_id = self.users.insert_one(user.model_dump(by_alias=True)).inserted_id
        return schemas.User.model_validate(self.get_user(user_id))

    def add_artist(self, artist: schemas.NewArtist) -> schemas.Artist:
        artist_dict = artist.model_dump(by_alias=True)
        artist_dict['events'] = [to_object_id(a_id) for a_id in artist_dict['events']]
        artist_id = self.artists.insert_one(artist_dict).inserted_id
        return schemas.Artist.model_validate(self.get_artist(artist_id))

    def get_artist(self, artist_id: str) -> schemas.Artist:
        artist = self.artists.find_one({'_id': to_object_id(artist_id)})
        return schemas.Artist.model_validate(artist)

    def get_artists(self):
        return [schemas.Artist.model_validate(artist) for artist in self.artists.find()]

    def add_artist_to_event(self, artist_id: str, event_id: str):
        self.artists.update_one({
            '_id': to_object_id(artist_id)},
            {'$push': {'events': to_object_id(event_id)}
             })
        self.events.update_one({
            '_id': to_object_id(event_id)},
            {'$push': {'artists': to_object_id(artist_id)}
             })

    def get_events(self):
        return [schemas.Event.model_validate(event) for event in self.events.find()]

    def get_top_users_for_venue(self, venue_id, order_by: OrderBy) -> list[schemas.VenueReport]:
        connect_with_user = {
            '$lookup': {
                'from': 'users',
                'localField': 'tickets.user_id',
                'foreignField': '_id',
                'as': 'user'
            }
        }
        group_by_user = {
            '$group': {
                '_id': '$user._id',
                'tickets': {
                    '$sum': 1
                },
                'user': {
                    '$addToSet': '$user'
                }
            }
        }
        cursor = self.events.aggregate([
            {'$match': {'venue_id': to_object_id(venue_id)}},
            {'$unwind': '$tickets'},
            connect_with_user,
            {'$unwind': '$user'},
            group_by_user,
            {'$unwind': '$user'},
            {'$sort': {'tickets': order_by.value}}
        ])
        return [schemas.VenueReport(
            user=schemas.User.model_validate(co['user']),
            tickets_purchased=co['tickets']
        ) for co in cursor]

    def get_user_by_email(self, user_name: str) -> schemas.User:
        user = self.users.find_one({'email': user_name})
        return schemas.User.model_validate(user)

    def add_ticket(self, ticket: schemas.NewTicket) -> schemas.Ticket:
        ticket_dict = ticket.model_dump(by_alias=True)
        ticket_dict['user_id'] = to_object_id(str(ticket_dict['user_id']))
        self.events.update_one({
            '_id': to_object_id(ticket.event_id)},
            {'$push': {'tickets': ticket_dict}
             })
        return self.get_ticket(ticket.user_id, ticket.event_id)

    def get_ticket(self, user_id: str, event_id: str | ObjectId) -> schemas.Ticket | None:
        event = self.events.find_one(
            {'_id': to_object_id(event_id), 'tickets.user_id': to_object_id(user_id)})
        if event is None:
            return event
        ticket = next(ticket for ticket in event["tickets"] if str(ticket["user_id"]) == str(user_id))
        return schemas.Ticket.model_validate(ticket)

    def return_ticket(self, user_id, event_id):
        self.events.update_one(
            {'_id': to_object_id(event_id), 'tickets.user_id': to_object_id(user_id)},
            {'$set': {'tickets.$.status': 'cancelled'}}
        )
        return

    def get_tickets(self) -> list[schemas.Ticket]:
        cursor = self.events.aggregate([{'$unwind': '$tickets'}])
        return [schemas.Ticket.model_validate(event['tickets']) for event in cursor]

    def get_event(self, event_id: str):
        event = self.events.find_one({'_id': to_object_id(event_id)})
        return schemas.Event.model_validate(event)

    def decrease_user_balance(self, user_id: str, amount: int):
        self.users.update_one({
            '_id': to_object_id(user_id)},
            {'$inc': {'balance': -1*amount}
             })

    def increase_user_balance(self, user_id: str, amount: int):
        self.users.update_one({
            '_id': to_object_id(user_id)},
            {'$inc': {'balance': amount}
             })

    def get_events_with_tickets(self) -> list[schemas.Event]:
        pass

    def get_event_with_tickets(self, ticket_id: str) -> schemas.Event:
        pass

    def add_event(self, event: schemas.NewEvent):
        event_dict = event.model_dump(by_alias=True)
        event_dict['venue_id'] = to_object_id(event_dict['venue_id'])
        event_dict['artists'] = [to_object_id(a_id) for a_id in event_dict['artists']]
        event_id = self.events.insert_one(event_dict).inserted_id
        return schemas.Event.model_validate(self.get_event(event_id))

    def add_venue(self, venue: schemas.NewVenue):
        venue_id = self.venues.insert_one(venue.model_dump(by_alias=True)).inserted_id
        return schemas.Venue.model_validate(self.get_venue(venue_id))

    def get_venue(self, venue_id: str):
        venue = self.venues.find_one({'_id': to_object_id(venue_id)})
        return schemas.Venue.model_validate(venue)

    def get_venues(self):
        return [schemas.Venue.model_validate(venue) for venue in self.venues.find()]

    def add_users(self, users: list[schemas.User]):
        self.users.insert_many([user.model_dump(by_alias=True) for user in users])

    def add_venues(self, venues: list[schemas.Venue]):
        self.venues.insert_many([venue.model_dump(by_alias=True) for venue in venues])

    def add_events(self, events: list[schemas.Event]):
        self.events.insert_many([event.model_dump(by_alias=True) for event in events])

    def add_artists(self, artists: list[schemas.Artist]):
        self.artists.insert_many([artist.model_dump(by_alias=True) for artist in artists])

    def get_tickets_for_user(self, user_id) -> list[schemas.UserTicket]:
        connect_with_user = {
            '$lookup': {
                'from': 'users',
                'localField': 'tickets.user_id',
                'foreignField': '_id',
                'as': 'user'
            }
        }
        cursor = self.events.aggregate(
            [{'$unwind': '$tickets'},
             connect_with_user,
             {'$match': {'user._id': to_object_id(user_id)}}, ])

        def create_response(co):
            ticket = schemas.Ticket.model_validate(co['tickets'])
            co['tickets'] = []
            return schemas.UserTicket(ticket=ticket,
                                      event=schemas.Event.model_validate(co))

        return [create_response(co) for co in cursor]

    def get_artist_info(self, artist_id: str) -> schemas.ArtistReport:
        pipeline = [
            {"$match": {"_id": to_object_id(artist_id)}},
            {'$unwind': '$events'},
            # connect wit events
            {
              '$lookup': {
                  'from': 'events',
                  'localField': 'events',
                  'foreignField': '_id',
                  'as': 'event'
              }
            },
            {'$unwind': '$event'},
            {'$unwind': '$event.tickets'},
            # {'$group': {
            #
            #     "number_of_events": {"$sum": 1},
            #     "number_of_booked_tickets": {
            #         "$sum": {
            #             "$cond": [{"$eq": ["$tickets.status", "booked"]}, 1, 0]
            #         }
            #     },
            # }}


            # {'$unwind', '$ticket'},
            # {
            #     "$lookup": {
            #         "from": "EventArtist",
            #         "localField": "_id",
            #         "foreignField": "right_id",
            #         "as": "event_artist"
            #     }
            # },
            # {
            #     "$unwind": "$event_artist"
            # },
            # {
            #     "$lookup": {
            #         "from": "Event",
            #         "localField": "event_artist.left_id",
            #         "foreignField": "_id",
            #         "as": "event"
            #     }
            # },
            # {
            #     "$unwind": "$event"
            # },
            # {
            #     "$lookup": {
            #         "from": "Ticket",
            #         "localField": "event._id",
            #         "foreignField": "event_id",
            #         "as": "ticket"
            #     }
            # },
            # {
            #     "$group": {
            #         "_id": "$_id",
            #         "first_name": {"$first": "$first_name"},
            #         "number_of_events": {"$sum": 1},
            #         "number_of_booked_tickets": {
            #             "$sum": {
            #                 "$cond": [{"$eq": ["$ticket.status", "booked"]}, 1, 0]
            #             }
            #         },
            #         "number_of_cancelled_tickets": {
            #             "$sum": {
            #                 "$cond": [{"$eq": ["$ticket.status", "cancelled"]}, 1, 0]
            #             }
            #         }
            #     }
            # }
        ]

        result = list(self.artists.aggregate(pipeline))

        data = result[0]

        return schemas.ArtistReport(
            artist_name=data['name'],
            number_of_events=data['number_of_events'],
            number_of_booked_tickets=data['number_of_booked_tickets'],
            number_of_cancelled_tickets=data['number_of_cancelled_tickets']
        )


    @property
    def events(self) -> pymongo.collection.Collection:
        return self.client.imse.events

    @property
    def users(self) -> pymongo.collection.Collection:
        return self.client.imse.users

    @property
    def artists(self) -> pymongo.collection.Collection:
        return self.client.imse.artists

    @property
    def venues(self) -> pymongo.collection.Collection:
        return self.client.imse.venues
