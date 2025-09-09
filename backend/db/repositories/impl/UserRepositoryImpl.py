from tortoise.exceptions import DoesNotExist
from tortoise import Tortoise
import datetime

from backend.db.models.entity.User import User
from backend.db.repositories.UserRepository import UserRepository

# 适合分布式




class UserRepositoryImpl(UserRepository):
    pass