import datetime
import uuid
from typing import List

from sqlalchemy import ForeignKey, Column, Table, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    _id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False, default='customer')
    profile_visibility: Mapped[str] = mapped_column(nullable=False, default='private')
    balance: Mapped[int] = mapped_column(nullable=False)
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="user")

    @property
    def id(self):
        return self._id


class Ticket(Base):
    __tablename__ = "ticket"
    # _id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("event._id"), nullable=False)
    event: Mapped["Event"] = relationship(back_populates="tickets")
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user._id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="tickets")
    purchase_date: Mapped[datetime.datetime] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default='booked')

    @property
    def _id(self):
        return str(self.user_id) + str(self.event_id)

    __table_args__ = (
        PrimaryKeyConstraint(
            user_id, event_id
        ),
    )


class Venue(Base):
    __tablename__ = "venue"
    _id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    capacity: Mapped[int] = mapped_column(nullable=False)
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
    name: Mapped[str] = mapped_column(nullable=False)
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="event")
    price: Mapped[int] = mapped_column(nullable=False)
    venue: Mapped["Venue"] = relationship(back_populates="events")
    venue_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("venue._id"), nullable=False)
    date: Mapped[datetime.datetime] = mapped_column(nullable=False)
    artists: Mapped[List["Artist"]] = relationship(
        secondary=EventArtist, back_populates="events")

    @property
    def id(self):
        return self._id


class Artist(Base):
    __tablename__ = "artist"
    _id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    stage_name: Mapped[str] = mapped_column(nullable=False)
    events: Mapped[List["Event"]] = relationship(secondary=EventArtist, back_populates="artists")

    @property
    def id(self):
        return self._id
