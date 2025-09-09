from fastapi import APIRouter, Body
import logging
from typing import Annotated
from pydantic import BaseModel, Field, model_validator
from enum import StrEnum, auto
from pandas import DataFrame
from backend.db.decorator.Cache import cache

from backend.db.interface import GetDataBaseInterface
from backend.db.result.Result import Result

from backend.db.models.dto.ExpClassDTO import ExpClassDTO
logger = logging.getLogger(__name__)
db_router = APIRouter()
db = GetDataBaseInterface()

class QueryType(StrEnum):
    exp_class = auto()
    exp_name = auto()
    sample_id = auto()


class TranscriptQuery(BaseModel):
    query_type: QueryType = Field(...,
                                  description="Type of query")
    query_value: tuple | None = Field(default=None,
                                      description="Values for the query. "
                                      "Optional for exp_class; required for exp_name / sample_id.")

    @model_validator(mode="before")
    def require_query_value_when_needed(cls, values):
        qt = values.get("query_type")
        qv = values.get("query_value")
        if qt in {QueryType.exp_name, QueryType.sample_id} and (not qv):
            raise ValueError(
                "query_value is required when query_type is exp_name or sample_id")
        return values


async def get_db_data(query_type: QueryType, query_value: tuple | None) -> DataFrame | None:
    match query_type:
        case QueryType.exp_class:
            logger.info("Fetching all experiment classes from the database.")
            return await db.get_exp_class()
        case QueryType.exp_name:
            logger.info(f"Fetching experiment with name: {query_value}")
            return await db.get_experiment(query_value)
        case QueryType.sample_id:
            logger.info(f"Fetching sample with ID: {query_value}")
            return await db.get_sample(query_value)
        case _:
            return None


@db_router.post("/transcripts/query")
# @cache(expire=3600,key_prefix="transcripts:exp_class")
async def query_transcripts(query: Annotated[TranscriptQuery, Body(...)]) -> Result:
    results = await get_db_data(query.query_type, query.query_value)
    if results is None or results.empty:
        logger.warning(f"No data found for query: {query}")
        return Result.error(
            message=f"No data found for query: {query}")
    # 序列化
    payload = Result.success(data=results.to_dict(orient="records"))
    logger.info(
        f"Successfully fetched query: {query}")
    return payload

@db_router.post("/transcripts/get_allexp_counts")
async def get_allexp_counts(expClassDTO: list[ExpClassDTO]) -> Result:
    res = await db.get_data_static(expClassDTO)
    return Result.success(res)