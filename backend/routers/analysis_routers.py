from fastapi import APIRouter, Request, Body
import logging
from typing import Annotated
from pydantic import BaseModel, Field, field_validator
import re

from backend.analysis.tpm_analysis import GeneDataAnalysis, AnalysisType


import pandas as pd


analysis_router = APIRouter()
logger = logging.getLogger(__name__)


def db_extract_gene_data(unique_ids: set[str], gene_name: set[str], type: AnalysisType) -> pd.DataFrame:
    """
    Placeholder function to extract gene data from the database.
    This should be replaced with actual database query logic.
    Args:
        unique_ids: Set of unique IDs to filter the data.
        gene_name: Set of gene names to filter the data.
    Returns:
        A pandas DataFrame containing the filtered gene data.
    """

    pass


class PlotParameter(BaseModel):
    """
    Base class for parameters used in analysis.
    This can be extended for specific analysis types.
    """
    width: int = Field(800, description="Width of the plot in pixels")
    height: int = Field(600, description="Height of the plot in pixels")


class GeneDataFilter(BaseModel):
    gene_name: set[str] = Field(..., description="Set of gene_id")
    unique_id: set[str] = Field(..., description="Set of uniqueID")
    analysis_type: AnalysisType = Field(...,
                                        description="Type of analysis to perform")
    plot_parameters: PlotParameter | None = Field(
        None, description="Parameters for the plot, if applicable")

    @field_validator("gene_name", mode="after")
    def validate_gene_name(cls, value):
        pattern = re.compile(r"^g\d{1,5}$")
        if not all(pattern.match(gene) for gene in value):
            raise ValueError(
                "gene_name must be a set of strings starting with 'g' followed by 1-5 digits")
        return value


async def tpm_analysis(request: Request, filters: GeneDataFilter):
    """
    Endpoint to perform TPM analysis on gene expression data.
    Args:
        request: FastAPI request object.
        filters: Filters for gene expression data analysis.
    Returns:
        Result of the TPM analysis.
    """
    logger.info("Received request for TPM analysis with filters: %s", filters)

    # Extracting parameters from the filters
    unique_ids = filters.unique_id
    gene_name = filters.gene_name
    analysis_type = filters.analysis_type
    logger.info(
        "Extracting gene data from the database\n"
        f"unique_ids: {unique_ids}, gene_name: {gene_name}, analysis_type: {analysis_type}")

    gene_data = db_extract_gene_data(unique_ids, gene_name, analysis_type)
    rprocessor = request.app.state.rprocessor

    analysis = GeneDataAnalysis(
        gene_data=gene_data,  # Placeholder for actual gene data
        analysis_type=analysis_type,
        rprocessor=rprocessor
    )

    return analysis.analysis()


# TODO:统一后端返回给前端的格式
@analysis_router.put("/transcripts/tpm",
                     description="Analysis for gene expression data")
async def tpm(request: Request,
              filters: Annotated[GeneDataFilter,
                                 Body(..., title="Gene expression data analysis filters")]):
    result = await tpm_analysis(request, filters)
    return {"result": str(result)}
