
from backend.db.models.dto.GeneExpressTpmDTO import GeneExpressTpmDTO
from backend.db.repositories.GeneExpressTpmRepository import GeneExpressTpmRepository


class GeneExpressTpmRepositoryImpl(GeneExpressTpmRepository):

    async def createOneGeneExpressTpm(self, body: GeneExpressTpmDTO) -> bool:
        result = await self.create(**body.__dict__)
        return bool(result)

    async def deleteOneGeneExpressTpm(self, unique_id: int) -> bool:
        result = await self.delete_by_id(unique_id)
        return bool(result)

    async def updateOneGeneExpressTpm(self, unique_id: int, body: GeneExpressTpmDTO) -> bool:
        data = body.dict(exclude_unset=True)
        result = await self.update_by_id(unique_id, **data)
        return bool(result)

    async def getOneGeneExpressTpm(self, unique_id: int) -> GeneExpressTpmDTO:
        result = await self.get_by_id(unique_id)
        return GeneExpressTpmDTO(**result.__dict__)
