from backend import schemas
from backend.sql.db import SqlDatabase
from backend import services


def test_sqldb():
    db = SqlDatabase(conn_url="sqlite:///./test.db")
    db.reset()
    db.add_user(schemas.NewUser(name="username"))
    users = db.get_users()
    assert users[0].id is not None
    assert users[0].name == "username"


# Untested: user cannot buy ticket twice
def test_buy_ticket():
    db = SqlDatabase(conn_url="sqlite:///./test.db")
    db.reset()
    service = services.EventService(db)
    db.add_venue(schemas.NewVenue(name='venue', city='Wien', capacity=2))
    db.add_user(schemas.NewUser(name='user 1', balance=20))
    venues = db.get_venues()
    db.add_event(schemas.NewEvent(name='event 1', price=10, venue_id=venues[0].id))
    users = db.get_users()
    user_id = users[0].id
    events = db.get_events()
    service.buy_ticket(user_id, events[0].id)
    events_with_tickets = db.get_events_with_tickets()
    user = db.get_user(user_id)
    assert len(events_with_tickets) == 1
    assert len(events_with_tickets[0].tickets) == 1
    assert user.balance == 10
