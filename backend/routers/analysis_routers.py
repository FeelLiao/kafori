from fastapi import APIRouter, Request, Body
import logging
from typing import Annotated, Any
from pydantic import BaseModel, Field
import pandas as pd

from backend.analysis.framework import get_analysis, catalog, InputData
from backend.db.interface import GetDataBaseInterface
from backend.api.utils import dataframe_long2wide
from backend.db.result.Result import Result  # 你的统一返回封装
# 确保在 app 启动时 import 一次插件目录，完成注册
import backend.analysis.plugins.pca  # noqa: F401

analysis_router = APIRouter()
logger = logging.getLogger(__name__)


class DataFilter(BaseModel):
    unique_id: set[str] = Field(..., description="UniqueEXID set")
    gene_name: set[str] = Field(..., description="Gene ID set")
    all_gene: bool = Field(
        False, description="Ignore gene_name and fetch all genes")


class AnalysisRequest(BaseModel):
    analysis: str = Field(..., description="Analysis id, e.g. pca")
    params: dict[str, Any] = Field(
        default_factory=dict, description="Analysis-specific params")
    data_filter: DataFilter


async def _fetch_gene_data(dfilt: DataFilter, kind: InputData) -> pd.DataFrame:
    db = GetDataBaseInterface()
    uids = tuple(dfilt.unique_id)
    genes = tuple(dfilt.gene_name)
    if kind == InputData.tpm:
        data = await db.get_gene_tpm(unique_id=uids, gene_id=genes, gene_id_is_all=dfilt.all_gene)
        logger.info(f"Fetched TPM data from database with shape {data.shape}")
    else:
        data = await db.get_gene_counts(unique_id=uids, gene_id=genes, gene_id_is_all=dfilt.all_gene)
        logger.info(
            f"Fetched Counts data from database with shape {data.shape}")
    return dataframe_long2wide(data)


@analysis_router.get("/transcripts/analysis/catalog", description="List available analyses and param schemas")
async def list_analyses():
    return Result.ok(data=catalog(), msg="OK")


@analysis_router.post("/transcripts/analysis", description="Run an analysis plugin")
async def run_analysis(request: Request, payload: Annotated[AnalysisRequest, Body(...)]):
    try:
        # 解析插件
        cls = get_analysis(payload.analysis)
        # 拉数
        gene_df = await _fetch_gene_data(payload.data_filter, cls.input_type)
        # 参数校验为插件声明的 Pydantic 模型
        params = cls.Params.model_validate(payload.params)
        # 执行
        logger.info(
            f"Running analysis: {cls.title} with params {cls.Params.model_dump(params)}")
        rproc = request.app.state.r_processor
        plugin = cls(df=gene_df, params=params, rproc=rproc)
        result = await plugin.run()
        return Result.ok(data=result, msg="OK")
    except KeyError as e:
        return Result.error(message=str(e))
    except Exception as e:
        logger.warning(f"Running analysis: {cls.title} failed")
        return Result.fail(msg=str(e))
