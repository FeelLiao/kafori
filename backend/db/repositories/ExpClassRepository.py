from backend.db.models.entity.ExpClass import ExpClass
from backend.db.models.dto.ExpClassDTO import ExpClassDTO
from .base import BaseRepository

from abc import ABC, abstractmethod


class ExpClassRepository(ABC, BaseRepository[ExpClass]):
    def __init__(self):
        super().__init__(ExpClass)

    @abstractmethod
    async def createOneExpClass(self, body: ExpClass) -> bool:
        ...

    @abstractmethod
    async def deleteOneExpClass(self, exp_class: int) -> bool:
        ...

    @abstractmethod
    async def updateOneExpClass(self, exp_class: int, body: ExpClass) -> bool:
        ...

    @abstractmethod
    async def getOneExpClass(self, exp_class: str) -> ExpClass:
        """
        查询实验类别表里面实验类别为category的数据，如果有则返回，没有就创建并返回
        Args:
           exp_class: 实验类别
        Returns:
            ExpClass: 实验类别
        """

        pass

    @abstractmethod
    async def getOneByCategory(self, category: str) -> ExpClassDTO:
        """
        分页查询实验类别
        Args:
            category: 实验类别
        Return:
            ExpClassDTO
        """
        pass


    # @abstractmethod
    # async def getExpClss(self, start_page: int, size: int) -> list[dict]:
    #     ...


# 单例
# sample_repo = ExpClassRepository()
