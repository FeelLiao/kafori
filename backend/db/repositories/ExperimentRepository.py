from backend.db.models.entity.Experiment import Experiment
from backend.db.models.dto.ExperimentDTO import ExperimentDTO
from .base import BaseRepository
from abc import ABC, abstractmethod

class ExperimentRepository(ABC, BaseRepository[Experiment]):
    def __init__(self):
        super().__init__(Experiment)

    @abstractmethod
    async def createOneExperiment(self, body: Experiment) -> bool:
        ...

    @abstractmethod
    async def deleteOneExperiment(self, unique_ex_id: int) -> bool:
        ...

    @abstractmethod
    async def updateOneExperiment(self, unique_ex_id: int, body:ExperimentDTO) -> bool:
        ...

    @abstractmethod
    async def getOneExperiment(self, unique_ex_id: int) -> ExperimentDTO:
        ...

    """
    查看ExperimentCategory 下的所有 Experiment
    """
    @abstractmethod
    async def getExperimentByCategory(self) -> list[dict]:
        ...

    @abstractmethod
    async def getExperimentCountsByExClass(self, exp_class: int) -> int:
        """
        Get all experiment counts according to exp_class.

        Args:
            exp_class: exp_class of ExpClass connect to ExperimentCategory
        Returns:
            int: containing all experiment counts according to exp_class.
        """
        ...

# 单例
# sample_repo = SampleRepository()