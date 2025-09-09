from backend.db.models.entity.User import User
from .base import BaseRepository

from abc import ABC, abstractmethod


class UserRepository(ABC, BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

