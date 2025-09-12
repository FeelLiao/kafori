from __future__ import annotations
from typing import Any, Dict, Type
from pydantic import BaseModel, Field
from enum import StrEnum
import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
import base64
from abc import abstractmethod, ABC
import logging

from backend.analysis.analysis_base import RProcessorPoolMP

logger = logging.getLogger(__name__)


class InputData(StrEnum):
    tpm = "tpm"
    counts = "counts"


class BaseAnalysisParams(BaseModel):
    # 所有分析共享的通用绘图参数，可被子类覆写/扩展
    width: int = Field(800, description="Plot width in px")
    height: int = Field(600, description="Plot height in px")


class BaseAnalysis(ABC):
    """
    统一分析插件基类：
    - id: 分析唯一标识
    - title: 友好名称
    - input_type: 需要的输入数据类型（tpm/counts）
    - Params: Pydantic 参数模型
    - run(...): 执行分析，返回 JSON 可序列化的 dict
    """
    id: str = "base"
    title: str = "Base Analysis"
    input_type: InputData = InputData.tpm
    Params: Type[BaseAnalysisParams] = BaseAnalysisParams

    def __init__(self, df: pd.DataFrame, params: BaseAnalysisParams, rproc: RProcessorPoolMP):
        self.df = df
        self.params = params
        self.rproc = rproc
        self.rdata = self.py2r(self.df)

    @staticmethod
    def str_to_base64(s: str) -> str:
        """Convert a string to base64 encoded string."""
        b64 = base64.b64encode(s.encode("utf-8")).decode("utf-8")
        logging.info("Converted string to base64.")
        return b64

    @staticmethod
    def py2r(df: pd.DataFrame) -> ro.RObject:
        with (ro.default_converter + pandas2ri.converter).context():
            res = ro.conversion.get_conversion().py2rpy(df)
            logger.info("Converted pandas DataFrame to R DataFrame.")
            return res

    @staticmethod
    def r2py(obj: ro.RObject) -> pd.DataFrame:
        with (ro.default_converter + pandas2ri.converter).context():
            res = ro.conversion.get_conversion().rpy2py(obj)
            logger.info("Converted R object to pandas DataFrame.")
            return res

    @abstractmethod
    async def run(self) -> Dict[str, Any]:
        """Run the analysis and return results as a JSON-serializable dict."""
        pass


# 注册表与装饰器
_registry: Dict[str, Type[BaseAnalysis]] = {}


def register_analysis(analysis_id: str):
    def _decorator(cls: Type[BaseAnalysis]):
        cls.id = analysis_id
        _registry[analysis_id] = cls
        return cls
    return _decorator


def get_analysis(analysis_id: str) -> Type[BaseAnalysis]:
    if analysis_id not in _registry:
        raise KeyError(f"Unknown analysis: {analysis_id}")
    return _registry[analysis_id]


def catalog() -> list[dict[str, Any]]:
    items = []
    for k, cls in _registry.items():
        items.append({
            "id": cls.id,
            "title": getattr(cls, "title", cls.id),
            "input_type": cls.input_type.value,
            "params_schema": cls.Params.model_json_schema()
        })
    return items
