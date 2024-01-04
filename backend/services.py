import datetime

from backend import schemas
from backend.database import Database
from backend.schemas import TicketStatus


class OutOfBalanceError(Exception):
    pass


class OutOfSpaceError(Exception):
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
        event_with_tickets = self.db.get_event_with_tickets(event_id)
        venue = self.db.get_venue(event_with_tickets.venue_id)

        if user.balance < event_with_tickets.price:
            raise OutOfBalanceError()
        if venue.capacity == len(event_with_tickets.tickets):
            raise OutOfSpaceError()

        self.db.add_ticket(ticket)
        self.db.decrease_user_balance(user_id, event_with_tickets.price)
