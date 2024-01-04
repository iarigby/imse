import datetime

from backend import schemas
from backend.sql.db import SqlDatabase
from backend import services

engine = SqlDatabase.engine(conn_url="sqlite:///./test.db")
SessionMaker = SqlDatabase.database(engine)


def test_sqldb():
    SqlDatabase.reset(engine)
    with SqlDatabase.session(SessionMaker) as db:
        db.add_user(schemas.NewUser(name="username"))
        users = db.get_users()
        assert users[0].id is not None
        assert users[0].name == "username"


# Untested: user cannot buy ticket twice
def test_buy_ticket():
    SqlDatabase.reset(engine)
    with SqlDatabase.session(SessionMaker) as db:
        service = services.EventService(db)
        db.add_venue(schemas.NewVenue(name='venue', city='Wien', capacity=2, events=[]))
        db.add_user(schemas.NewUser(name='user 1', balance=20))
        venues = db.get_venues()
        db.add_event(schemas.NewEvent(name='event 1',
                                      price=10,
                                      venue_id=venues[0].id,
                                      date=datetime.datetime.now(),
                                      tickets=[],
                                      artists=[]))
        users = db.get_users()
        user_id = users[0].id
        events = db.get_events()
        service.buy_ticket(user_id, events[0].id)

    with SqlDatabase.session(SessionMaker) as db:
        events = db.get_events()
        user = db.get_user(user_id)
        assert len(events) == 1
        assert len(events[0].tickets) == 1
        assert user.balance == 10
