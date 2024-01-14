import datetime
import timedelta
import streamlit as st


from backend import schemas
from backend.database import Database


class OutOfBalanceError(BaseException):
    pass


class OutOfSpaceError(BaseException):
    pass


class UserAlreadyHasTicket(BaseException):
    pass


class LateCancelation(BaseException):
    pass


class EventService:
    db: Database

    def __init__(self, db: Database):
        self.db = db

    def buy_ticket(self, user_id: str, event_id: str):
        if self.db.get_ticket(user_id, event_id) is not None:
            raise UserAlreadyHasTicket()
        ticket = schemas.NewTicket(
            purchase_date=datetime.datetime.now(),
            status='booked',
            user_id=user_id,
            event_id=event_id
        )

        user = self.db.get_user(user_id)
        event = self.db.get_event(event_id)
        venue = self.db.get_venue(event.venue_id)

        if user.balance < event.price:
            raise OutOfBalanceError()
        if venue.capacity == len(event.tickets):
            raise OutOfSpaceError()

        self.db.add_ticket(ticket)
        self.db.decrease_user_balance(user_id, event.price)

    def cancel_ticket(self, user_id: str, event_id: str):
        ticket = self.db.get_ticket(user_id, event_id)
        event = self.db.get_event(event_id=ticket.event_id)
        event_date = event.date
        current_date = datetime.datetime.now()
        two_weeks_ago = event_date - timedelta.Timedelta(weeks=2)
        if current_date > two_weeks_ago:
            raise LateCancelation()
        self.db.return_ticket(user_id, event_id)
        self.db.increase_user_balance(user_id, event.price)

        # self.db.add_ticket(ticket)

