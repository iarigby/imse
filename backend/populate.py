import random

from backend.database import Database

from dataclasses import dataclass
from backend import generate, services


@dataclass
class Config:
    artists: int = 5
    users: int = 20
    venues: int = 10
    venue_capacity: (int, int) = (20, 200)
    events: int = 10


default_config = Config()


# need to check event existing tickets less than capacity
def populate_database(db: Database, config: Config = default_config):
    fixed_user1 = generate.user()
    fixed_user1.email = "user1@example.org"
    fixed_user1.password = "sample_password"
    fixed_user1.first_name = "Barbara"
    fixed_user1.last_name = "Dalton"
    fixed_user1.balance = 200

    admin_user = generate.user()
    admin_user.email = "admin"
    admin_user.password = "sample_password"
    admin_user.first_name = "admin"
    admin_user.last_name = "admin"
    admin_user.balance = 200
    db.add_user(admin_user)
    db.add_user(fixed_user1)

    for user in range(config.users):
        db.add_user(generate.user())

    for venue in range(config.venues):
        db.add_venue(generate.venue())

    for artist in range(config.artists):
        db.add_artist(generate.artist())

    venues = db.get_venues()
    users = db.get_users()
    service = services.EventService(db)

    for venue in venues:
        for event_i in range(config.events):
            event = db.add_event(generate.event(venue.id))
            for i in range(random.randint(0, 10)):
                try:
                    service.buy_ticket(random.choice(users).id, event.id)
                except services.OutOfSpaceError:
                    pass
                except services.OutOfBalanceError:
                    pass
                except services.UserAlreadyHasTicket:
                    pass

    artists = db.get_artists()
    events = db.get_events()

    for artist in artists:
        for i in range(random.randint(0, config.events)):
            db.add_artist_to_event(artist.id, events[i].id)

