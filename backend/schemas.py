from pydantic import BaseModel


class NewUser(BaseModel):
    name: str

    class Config:
        from_attributes = True


class User(NewUser):
    _id: int


class Ticket(BaseModel):
    _id: int

    class Config:
        from_attributes = True


class Concert(BaseModel):
    _id: int
    name: str

    class Config:
        from_attributes = True


class ConcertWithTickets(Concert):
    tickets: list[Ticket]
