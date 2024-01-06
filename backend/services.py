import datetime

from backend import schemas
from backend.database import Database
from backend.schemas import TicketStatus


class OutOfBalanceError(BaseException):
    pass


class OutOfSpaceError(BaseException):
    pass


class EventService:
    db: Database

    def __init__(self, db: Database):
        self.db = db

    def buy_ticket(self, user_id: str, event_id: str):
        ticket = schemas.NewTicket(
            purchase_date=datetime.datetime.now(),
            status=TicketStatus.BOOKED,
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
