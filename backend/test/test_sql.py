from backend import generate
from backend.sql.db import SqlDatabase
from backend import services

engine = SqlDatabase.engine(conn_url="sqlite:///./test.db")
SessionMaker = SqlDatabase.database(engine)


def test_sqldb():
    SqlDatabase.reset(engine)
    with SqlDatabase.session(SessionMaker) as db:
        new_user = generate.user()
        db.add_user(new_user)
        users = db.get_users()
        assert users[0].id is not None
        assert users[0].first_name == new_user.first_name


# Untested: user cannot buy ticket twice
def test_buy_ticket():
    SqlDatabase.reset(engine)
    with SqlDatabase.session(SessionMaker) as db:
        service = services.EventService(db)
        db.add_venue(generate.venue())
        db.add_user(generate.user(balance=20))
        venues = db.get_venues()
        db.add_event(generate.event(venues[0].id, price=10))
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
