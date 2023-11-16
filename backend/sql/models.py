import uuid
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    _id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(unique=True)
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="user")

    @property
    def id(self):
        return self._id


class Ticket(Base):
    __tablename__ = "ticket"
    _id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    concert_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("concert._id"))
    concert: Mapped["Concert"] = relationship(back_populates="tickets")
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user._id"))
    user: Mapped["User"] = relationship(back_populates="tickets")

    @property
    def id(self):
        return self._id


class Concert(Base):
    __tablename__ = "concert"
    _id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="concert")

    @property
    def id(self):
        return self._id
