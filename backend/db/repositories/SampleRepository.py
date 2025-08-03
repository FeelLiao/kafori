from datetime import date
from typing import Optional

from backend.db.models.entity.Sample import Sample
from .base import BaseRepository
from backend.db.models.dto.SampleDTO import SampleDTO
from abc import ABC, abstractmethod

class SampleRepository(ABC, BaseRepository[Sample]):
    def __init__(self):
        super().__init__(Sample)

    """
    ** 插入一个sample对象
    @:param body SampleCreate  #传入的sample对象实体
    """
    @abstractmethod
    async def createOneSample(self, body: SampleDTO) -> bool:
        ...

    @abstractmethod
    async def deleteOneSample(self, unique_id: int) -> bool:
        ...

    @abstractmethod
    async def updateOneSample(self, unique_id: int, body:SampleDTO) -> bool:
        ...

    @abstractmethod
    async def getOneSample(self, unique_id: int) -> SampleDTO:
        ...

    @abstractmethod
    async def getSampleBySampleID(self, sample_id: str) -> SampleDTO | None:
        ...

    """
    查看某个 Experiment 下的所有样本（带年龄/部位）
    :param unique_ex_id: experiment表中的实验唯一id
    :return list[dict] : 列表和字典组合类型对应前端的列表和json组合类型
    """
    @abstractmethod
    async def getSampleByUniqueExId(self, unique_ex_id: str) -> list[dict]:
        ...

    """
    根据采集部位 collection_part 和时间范围查询样本
    :param collection_part: 部位名；None 表示不限
    :param start_time:      起始日期（包含）；None 表示不限
    :param end_time:        结束日期（包含）；None 表示不限
    :return: 样本字典列表
    """
    @abstractmethod
    async def getSampleByPartTime(
            self,
            collection_part: Optional[str] = None,
            start_time: Optional[date] = None,
            end_time: Optional[date] = None,
    ) -> list[dict]:
        ...

    """
    按年龄、时间、部位范围查询样本
    :param min_age:  最小年龄（含）
    :param max_age:  最大年龄（含）
    :param start_time: collection_time 起始（含）
    :param end_time:   collection_time 结束（含）
    :param collection_part: 部位名；None 为不限
    :return: 字典列表，按 collection_time 倒序
    """
    @abstractmethod
    async def getSampleByAgeTimePart(
        self,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        start_time: Optional[date] = None,
        end_time: Optional[date] = None,
        collection_part: Optional[str] = None,
    ) -> list[dict]:
        ...

# 单例
# sample_repo = SampleRepository()