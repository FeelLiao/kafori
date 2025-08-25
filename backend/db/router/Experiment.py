from fastapi import APIRouter,Request

from backend.db.repositories.impl.ExperimentRepositoryImpl import ExperimentRepositoryImpl
from backend.db.models.dto.ExperimentDTO import ExperimentDTO
from backend.db.result.Result import Result

router = APIRouter(prefix="/experiment", tags=["Experiment"])

experimentRepository = ExperimentRepositoryImpl()

# 2. 创建实验
"""
{
    "unique_ex_id": 2024001,
    "exp_class": 1,
    "experiment": "Leaf_2024_rep1"
}
"""


@router.post("/")
async def createOneExperiment(body: ExperimentDTO):

    exp = await experimentRepository.createOneExperiment(body)
    if exp:
        return Result.success(body)

@router.delete("/")
async def deleteOneExperiment(unique_ex_id: int) :
    result = await experimentRepository.deleteOneExperiment(unique_ex_id)
    if result:
        return Result.success()
    else:
        return Result.error()

@router.put("/")
async def updateOneExperiment(unique_ex_id: int, body: ExperimentDTO):
    print(body.__dict__)

    result = await experimentRepository.updateOneExperiment(unique_ex_id, body)
    if result:
        return Result.success()
    else:
        return Result.error()

@router.get("/")
async def getOneExperiment(unique_ex_id: int) :
    result = await experimentRepository.getOneExperiment(unique_ex_id)
    if result:
        return Result.success(result)
    else:
        return Result.error()




