import pytest
from backend.db.repositories.impl.ExpClassRepositoryImpl import ExpClassRepositoryImpl


expclass = ExpClassRepositoryImpl()


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
