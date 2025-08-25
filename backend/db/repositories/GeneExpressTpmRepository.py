from backend.db.models.entity.GeneExpressTpm import GeneExpressTpm
from backend.db.models.dto.GeneExpressTpmDTO import GeneExpressTpmDTO
from .base import BaseRepository
from abc import ABC, abstractmethod

class GeneExpressTpmRepository(ABC, BaseRepository[GeneExpressTpm]):
    def __init__(self):
        super().__init__(GeneExpressTpm)

    @abstractmethod
    async def createOneGeneExpressTpm(self, body: GeneExpressTpmDTO) -> bool:
        ...

    @abstractmethod
    async def deleteOneGeneExpressTpm(self, unique_id: int) -> bool:
        ...

    @abstractmethod
    async def updateOneGeneExpressTpm(self, unique_id: int, body:GeneExpressTpmDTO) -> bool:
        ...

    @abstractmethod
    async def getOneGeneExpressTpm(self, unique_id: int) -> GeneExpressTpmDTO:
        ...