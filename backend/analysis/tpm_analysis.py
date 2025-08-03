from rpy2.robjects import pandas2ri
import rpy2.robjects as ro
from typing import Any
from enum import StrEnum, auto
import pandas as pd
import base64

from backend.analysis.analysis_base import RProcessorPoolMP
from backend.analysis.scripts.pca import pca_code


class DataType(StrEnum):
    r2py = "r2py"
    py2r = "py2r"


class AnalysisType(StrEnum):
    deg = auto()
    pca = auto()
    tpm_heatmap = auto()


class GeneDataAnalysis:
    """Class for gene data analysis using R."""

    def __init__(self, gene_data: pd.DataFrame,
                 analysis_type: AnalysisType,
                 rprocessor: RProcessorPoolMP):
        self.data = gene_data
        self.type = analysis_type
        self.rprocessor = rprocessor
        self.rdata = GeneDataAnalysis.rpy_convertor(self.data, DataType.py2r)

    @staticmethod
    def str_to_base64(s: str) -> str:
        """Convert a string to base64 encoded string."""
        b64 = base64.b64encode(s.encode("utf-8")).decode("utf-8")
        return b64

    @staticmethod
    def rpy_convertor(df: Any, data_type: DataType) -> Any:
        """ Convert between R data frame and pandas DataFrame.
        Args:
            df: R data frame to convert.
            data_type: Type of conversion, either r2py or py2r.
        Returns:
            Converted pandas DataFrame or R data frame.
        """
        if data_type == DataType.r2py:
            with (ro.default_converter + pandas2ri.converter).context():
                return ro.conversion.get_conversion().rpy2py(df)
        elif data_type == DataType.py2r:
            with (ro.default_converter + pandas2ri.converter).context():
                return ro.conversion.get_conversion().py2rpy(df)

    async def analysis(self) -> Any:
        """
        Perform the analysis based on the analysis type.
        Args:
            type: Type of analysis to perform.
        Returns:
            Result of the analysis.
        """
        match self.type:
            case AnalysisType.deg:
                return await self.run_deg()
            case AnalysisType.pca:
                return await self.run_pca()
            case AnalysisType.tpm_heatmap:
                return await self.run_tpm_heatmap()
            case _:
                raise ValueError(f"Unsupported analysis type: {type}")

    async def run_pca(self) -> dict[str, Any]:
        """
        Run PCA analysis.
        """
        run_result = await self.rprocessor.run_analysis(pca_code,
                                                        expression_tpm=self.rdata)
        pca_plot = GeneDataAnalysis.str_to_base64(
            run_result.rx2("pca_plot")[0])
        pca_eig = GeneDataAnalysis.rpy_convertor(
            run_result.rx2("pca_eig"), DataType.r2py)
        pca_sample = GeneDataAnalysis.rpy_convertor(
            run_result.rx2("pca_sample"), DataType.r2py)

        return {
            "pca_plot": pca_plot,
            "pca_eig": pca_eig,
            "pca_sample": pca_sample
        }

    async def run_deg(self) -> Any:
        pass

    async def run_tpm_heatmap(self) -> Any:
        pass
