from fastapi import APIRouter, Request, Body
import logging
from typing import Annotated
from pydantic import BaseModel, Field

from backend.db.interface import GetDataBaseInterface

logger = logging.getLogger(__name__)
db_router = APIRouter()


class TranscriptQuery(BaseModel):
    query_type: str = Field(...,
                            description="Type of query, e.g., 'by_id', 'by_name'")
    query_value: str = Field(...,
                             description="Value to query, e.g., transcript ID or name")

# @db_router.post("/transcripts/query")
# async def query_transcripts(request: Request, query: Annotated[TranscriptQuery, Body(embed=True,
#     description="A comma-separated list of transcript IDs to query.", example="ENST00000335137,ENST00000423372")]):
#     """
#     Query the database for specific transcript IDs.
#     Args:
#         request (Request): The FastAPI request object.
#         query (str): A comma-separated list of transcript IDs.
#     Returns:
#         dict: A dictionary containing the query results.
#     """
#     try:
#         db = request.app.state.db
#         transcript_ids = [tid.strip() for tid in query.split(",") if tid.strip()]
#         if not transcript_ids:
#             return {"error": "No valid transcript IDs provided."}

#         logger.info(f"Querying database for transcript IDs: {transcript_ids}")
#         results = await db
