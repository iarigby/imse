from sqlalchemy import MetaData, Table, event
from sqlalchemy.schema import CreateTable
from backend.sql.db import SqlDatabase
from backend.sql import models

metadata_obj = MetaData()


@event.listens_for(metadata_obj, "column_reflect")
def genericize_datatypes(inspector, tablename, column_dict):
    column_dict["type"] = column_dict["type"].as_generic()


def main():

    engine = SqlDatabase.engine()
    try:
        models.Base.metadata.create_all(engine)
    except:
        pass

    for DbTable in [models.User, models.Ticket, models.Venue, models.Event, models.Artist]:

        my_sql_table = Table(DbTable.__tablename__, metadata_obj, autoload_with=engine)

        print(CreateTable(my_sql_table).compile(engine))
