from datetime import date

import pytest
from backend.db.repositories.impl.SampleRepositoryImpl import SampleRepositoryImpl
# from src.db.models.dto.SampleDTO import SampleDTO
# from tortoise import Tortoise

sample = SampleRepositoryImpl()


# ---------- 5. 测试函数 ----------

@pytest.mark.asyncio
async def test_getSampleByAgeTimePart():

    await sample.getSampleByAgeTimePart(min_age=20, max_age=30)
    await sample.getSampleByAgeTimePart(min_age=10,
                                        max_age=50,
                                        start_time=date(2022, 1, 1),
                                        end_time=date(2023, 12, 31))
    result = await sample.getSampleByAgeTimePart(min_age=25,
                                                 max_age=25,
                                                 start_time=date(1911, 6, 1),
                                                 end_time=date(2011, 7, 1),
                                                 collection_part="main stem")
    print(result)
