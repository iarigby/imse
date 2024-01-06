from backend.sql.db import SqlDatabase


engine = SqlDatabase.engine(conn_url="sqlite:///./test.db")
SessionMaker = SqlDatabase.database(engine)
