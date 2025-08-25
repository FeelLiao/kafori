
from fastapi import APIRouter

from backend.db.repositories.impl.SampleRepositoryImpl import SampleRepositoryImpl
from backend.db.result.Result import Result
from backend.db.models.dto.SampleDTO import SampleDTO, SampleCreate


router = APIRouter(prefix="/sample", tags=["Sample"])

sampleRepository = SampleRepositoryImpl()

"""
{
    "unique_id": 10001,
    "unique_ex_id": 2024001,
    "sample_id": "L001-01",
    "collection_time": "2024-05-17",
    "collection_part": "leaf",
    "sample_age": 30
}
"""
# data = {
#     "unique_id": 10001,
#     "unique_ex_id": 2024001,
#     "sample_id": "L001-01",
#     "collection_time": "2024-05-17",
#     "collection_part": "leaf",
#     "sample_age": 30
# }


@router.post("/")
async def create_sample(body: SampleDTO):
    samp = await sampleRepository.createOneSample(body)
    if samp:
        return Result.success(body)


@router.delete("/")
async def deleteOneExperiment(unique_id: int):
    result = await sampleRepository.deleteOneSample(unique_id)
    if result:
        return Result.success()
    else:
        return Result.error()


@router.put("/")
async def updateOneExperiment(unique_id: int, body: SampleDTO):
    print(body.__dict__)

    result = await sampleRepository.updateOneSample(unique_id, body)
    if result:
        return Result.success()
    else:
        return Result.error()


@router.get("/")
async def getOneExperiment(unique_id: int):
    result = await sampleRepository.getOneSample(unique_id)
    if result:
        return Result.success(result)
    else:
        return Result.error()
