from backend import schemas
from backend.sql.db import SqlDatabase


def test_sqldb():
    db = SqlDatabase(conn_url="sqlite:///./test.db")
    db.reset()
    db.add_user(schemas.User(name="username"))
    users = db.get_users()
    assert users[0].name == "username"
