from tortoise import Tortoise

from backend.db.models.dto.ExperimentDTO import ExperimentDTO
from backend.db.repositories.ExperimentRepository import ExperimentRepository
class ExperimentRepositoryImpl(ExperimentRepository):

    async def createOneExperiment(self, body: ExperimentDTO) -> bool:
        result = await self.create(**body.__dict__)
        return bool(result)

    async def deleteOneExperiment(self, unique_ex_id: int) -> bool:
        result = await self.delete_by_id(unique_ex_id)
        return bool(result)

    async def updateOneExperiment(self, unique_ex_id: int, body:ExperimentDTO) -> bool:
        data = body.dict(exclude_unset=True)
        result = await self.update_by_id(unique_ex_id, **data)
        return bool(result)

    async def getOneExperiment(self, unique_ex_id: int) -> ExperimentDTO:
        result = await self.get_by_id(unique_ex_id)
        return ExperimentDTO(**result.__dict__)

    async def getExperimentByCategory(self) -> list[dict]:
        sql = """
            SELECT ec.experiment_category as ExperimentCategory,
                   e.unique_ex_id as UniqueEXID,
                   e.experiment as Experiment
            FROM experiment e
            JOIN exp_class ec ON e.exp_class = ec.exp_class
            ORDER BY ec.experiment_category, e.unique_ex_id;
        """
        conn = Tortoise.get_connection("default")
        return await conn.execute_query_dict(sql)

    async def getExperimentCountsByExClass(self, exp_class: int) -> int:
        counts = await self.model.filter(ExpClass =exp_class).count()


