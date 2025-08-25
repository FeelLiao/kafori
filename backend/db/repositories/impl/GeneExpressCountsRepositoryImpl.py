
from backend.db.models.dto.GeneExpressCountsDTO import GeneExpressCountsDTO
from backend.db.repositories.GeneExpressCountsRepository import GeneExpressCountsRepository


class GeneExpressCountsRepositoryImpl(GeneExpressCountsRepository):

    async def createOneGeneExpressCounts(self, body: GeneExpressCountsDTO) -> bool:
        result = await self.create(**body.__dict__)
        return bool(result)

    async def deleteOneGeneExpressCounts(self, unique_id: int) -> bool:
        result = await self.delete_by_id(unique_id)
        return bool(result)

    async def updateOneGeneExpressCounts(self, unique_id: int, body: GeneExpressCountsDTO) -> bool:
        data = body.dict(exclude_unset=True)
        result = await self.update_by_id(unique_id, **data)
        return bool(result)

    async def getOneGeneExpressCounts(self, unique_id: int) -> GeneExpressCountsDTO:
        result = await self.get_by_id(unique_id)
        return GeneExpressCountsDTO(**result.__dict__)
