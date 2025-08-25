from fastapi import APIRouter

from backend.db.repositories.impl.ExpClassRepositoryImpl import ExpClassRepositoryImpl
from backend.db.models.dto.ExpClassDTO import ExpClassDTO

from backend.db.result.Result import Result

router = APIRouter(prefix="/exp_class", tags=["ExpClass"])


expclass = ExpClassRepositoryImpl()

# data = {
#     "exp_class": 1,
#     "experiment_category": "RNA-seq"
# }


@router.post("/")
async def create_demo(body: ExpClassDTO):
    # # 1. 创建实验类别
    cls1 = await expclass.createOneExpClass(body)
    if cls1:
        return Result.success(body)


@router.delete("/")
async def deleteOneExpClass(exp_class: int):
    result = await expclass.deleteOneExpClass(exp_class)
    if result:
        return Result.success()
    else:
        return Result.error()


@router.put("/")
async def updateOneExpClass(exp_class: int, body: ExpClassDTO):
    print(body.__dict__)

    result = await expclass.updateOneExpClass(exp_class, body)
    if result:
        return Result.success()
    else:
        return Result.error()


@router.get("/")
async def getOneExpClass(exp_class: str):
    result = await expclass.getOneExpClass(exp_class)
    if result:
        return Result.success(result.__dict__)
    else:
        return Result.error()
