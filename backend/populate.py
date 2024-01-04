from backend.database import Database

from dataclasses import dataclass
from backend import generate


@dataclass
class Config:
    artists: int = 5
    users: int = 10
    venues: int = 10
    venue_capacity: (int, int) = (20, 200)
    events: int = 10


default_config = Config()


# need to check event existing tickets less than capacity
def populate_database(db: Database, config: Config = default_config):
    for user in range(config.users):
        db.add_user(generate.user())
