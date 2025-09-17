import pytest
from backend.db.models.dto.ExpClassDTO import ExpClassDTO
from backend.db.repositories.impl.ExpClassRepositoryImpl import ExpClassRepositoryImpl
from backend.db.interface import GetDataBaseInterface as database
from backend.db.interface import PutDataBaseInterface as put_db

expclass = ExpClassRepositoryImpl()
# database = GetDataBaseInterface()

# ---------- 5. 测试函数 ----------

"""
通过UploadFileProcessor.experiment_categories属性搜索数据库中的实验类别，返回
expc={"ExperimentCategory":"ExpClass"}
1. 有的话则返回 ExpClass 字段的值
2. 没有的话则根据规则新建一个ExpClass 字段的值，并返回
"""


@pytest.mark.asyncio
async def test_getOneByCategory():

    dto = await expclass.getOneByCategory("DH4")
    print(dto.ExpClass)

@pytest.mark.asyncio
async def test_get_exp_class():
    data = await database.get_exp_class()
    print(data)

@pytest.mark.asyncio
async def test_put_exp_class():
    test_data = [{"ExpClass": "e2", "ExperimentCategory": "dormant2"},
                 {"ExpClass": "e3", "ExperimentCategory": "dormant3"}]
    data = await put_db.exclass_processing(test_data)
    print(data)

# @pytest.mark.asyncio
# async def test_get_exp_classes():
#     test_data = [
#         {
#             "ExpClass": "e1",
#             "ExperimentCategory": "position effect"
#         },
#         {
#             "ExpClass": "e2",
#             "ExperimentCategory": "dormant2"
#         },
#         {
#             "ExpClass": "e3",
#             "ExperimentCategory": "dormant3"
#         },
#         {
#             "ExpClass": "EXPC68b840a9001",
#             "ExperimentCategory": "drought"
#         },
#         {
#             "ExpClass": "LRX20250825c3106917",
#             "ExperimentCategory": "DH4"
#         }
#     ]
#
#     # 将字典列表转换为 ExpClassDTO 对象列表
#     expClassDTO_list = [ExpClassDTO.parse_obj(item) for item in test_data]
#
#     data = await put_db.get_data_static(expClassDTO_list)
#     print(data)