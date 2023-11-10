from abc import ABC, abstractmethod

from backend import schemas


class Database(ABC):
    @abstractmethod
    def get_users(self) -> list[schemas.User]:
        pass

    @abstractmethod
    def add_user(self, user: schemas.NewUser):
        pass

    @abstractmethod
    def reset(self):
        pass

