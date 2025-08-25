from datetime import date

import pytest
from backend.db.repositories.impl.SampleRepositoryImpl import SampleRepositoryImpl

sample = SampleRepositoryImpl()
from backend.db.interface import GetDataBaseInterface

database = GetDataBaseInterface()


class CollectionDate:
    starttime: date
    endtime: date


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


@pytest.mark.asyncio
async def test_get_sample():
    unique_ex_id = ("p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8")
    collection_part = ("main stem", "main stem2")
    start_time = date(2001, 1, 1)
    end_time = date(2025, 12, 31)

    collect_time = CollectionDate()
    collect_time.starttime = start_time
    collect_time.endtime = end_time

    res = await database.get_sample(unique_ex_id, collect_time, collection_part)
    print(res)
