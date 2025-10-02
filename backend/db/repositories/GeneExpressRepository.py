from backend.db.models.entity.GeneExpress import GeneExpress
from .base import BaseRepository
from abc import ABC,abstractmethod

class GeneExpressRepository(ABC, BaseRepository[GeneExpress]):
    def __init__(self):
        super().__init__(GeneExpress)

