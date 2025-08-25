from backend.db.models.entity.GeneExpressCounts import GeneExpressCounts
from backend.db.models.dto.GeneExpressCountsDTO import GeneExpressCountsDTO
from .base import BaseRepository
from abc import ABC,abstractmethod

class GeneExpressCountsRepository(ABC, BaseRepository[GeneExpressCounts]):
    def __init__(self):
        super().__init__(GeneExpressCounts)

    @abstractmethod
    async def createOneGeneExpressCounts(self, body: GeneExpressCountsDTO) -> bool:
        ...

    @abstractmethod
    async def deleteOneGeneExpressCounts(self, unique_id: int) -> bool:
        ...

    @abstractmethod
    async def updateOneGeneExpressCounts(self, unique_id: int, body:GeneExpressCountsDTO) -> bool:
        ...

    @abstractmethod
    async def getOneGeneExpressCounts(self, unique_id: int) -> GeneExpressCountsDTO:
        ...