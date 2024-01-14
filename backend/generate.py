import random
import uuid
from typing import Optional

from backend import schemas
from faker import Faker

fake = Faker()
it_f = Faker('it_IT')


def venue() -> schemas.NewVenue:
    city = fake.city()
    word = fake.street_suffix()

    names = [
        word + ' ' + city,
        fake.street_name(),
        word + ' ' + fake.company_suffix()
    ]
    return schemas.NewVenue(name=random.choice(names),
                            city=city,
                            capacity=random.randint(20, 10000),
                            events=[])


def event(venue_id: str | uuid.UUID,
          price: Optional[int] = None,
          artists: Optional[list[str | uuid.UUID]] = None) -> schemas.NewEvent:
    return schemas.NewEvent(name=f"{it_f.city_prefix()} {it_f.city()} {it_f.city_suffix()}",
                            price=price or random.randint(0, 50),
                            venue_id=venue_id,
                            date=fake.future_date(),
                            artists=artists or [],
                            tickets=[])


def ticket(user_id: str | uuid.UUID,
           event_id: str | uuid.UUID) -> schemas.NewTicket:
    return schemas.NewTicket(purchase_date=fake.past_datetime().replace(microsecond=0),
                             status=random.choice(['purchased', 'cancelled']),
                             user_id=user_id,
                             event_id=event_id)


def artist() -> schemas.NewArtist:
    return schemas.NewArtist(first_name=fake.unique.first_name(),
                             last_name=fake.last_name(),
                             stage_name=fake.color_name() + ' ' + fake.first_name_female())


def user(balance: int | None = None) -> schemas.NewUser:
    return schemas.NewUser(first_name=fake.unique.first_name(),
                           last_name=fake.last_name(),
                           email=fake.email(),
                           password=fake.password(),
                           role='customer',
                           profile_visibility=random.choice(['public', 'private']),
                           balance=balance or random.randint(100, 500))
