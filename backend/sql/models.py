import datetime
import uuid
from typing import List

from sqlalchemy import ForeignKey, Enum, Column, Table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

from backend import schemas


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    _id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    role = Column(Enum(schemas.UserRole))
    profile_visibility = Column(Enum(schemas.ProfileVisibility))
    balance: Mapped[int]
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="user")

    @property
    def id(self):
        return self._id


class Ticket(Base):
    __tablename__ = "ticket"
    _id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("event._id"))
    event: Mapped["Event"] = relationship(back_populates="tickets")
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user._id"))
    user: Mapped["User"] = relationship(back_populates="tickets")
    purchase_date: Mapped[datetime.datetime]
    status = Column(Enum(schemas.TicketStatus))

    @property
    def id(self):
        return self._id


class Venue(Base):
    __tablename__ = "venue"
    _id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str]
    city: Mapped[str]
    capacity: Mapped[int]
    events: Mapped[List["Event"]] = relationship(back_populates="venue")

    @property
    def id(self):
        return self._id


EventArtist = Table(
    "event_artist",
    Base.metadata,
    Column("left_id", ForeignKey("event._id")),
    Column("right_id", ForeignKey("artist._id")),
)


class Event(Base):
    __tablename__ = "event"
    _id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str]
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="event")
    price: Mapped[int]
    venue: Mapped["Venue"] = relationship(back_populates="events")
    venue_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("venue._id"))
    date: Mapped[datetime.datetime]
    artists: Mapped[List["Artist"]] = relationship(
        secondary=EventArtist, back_populates="events")

    @property
    def id(self):
        return self._id


class Artist(Base):
    __tablename__ = "artist"
    _id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str]
    events: Mapped[List["Event"]] = relationship(secondary=EventArtist, back_populates="artists")
