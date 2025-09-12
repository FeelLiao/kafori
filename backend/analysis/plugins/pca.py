from typing import Any, Dict
from pydantic import Field

from backend.analysis.framework import BaseAnalysis, BaseAnalysisParams, InputData, register_analysis
from backend.analysis.scripts.pca import pca_code  # 现有 R 脚本


class PCAParams(BaseAnalysisParams):
    ncps: int = Field(
        5, ge=2, le=20, description="Number of principal components")


@register_analysis("pca")
class PCAAnalysis(BaseAnalysis):
    title = "PCA"
    input_type = InputData.tpm
    Params = PCAParams

    async def run(self) -> Dict[str, Any]:
        res = await self.rproc.run_analysis(
            pca_code,
            expression_tpm=self.rdata,
            width=self.params.width,
            height=self.params.height,
            ncps=int(self.params.ncps),
        )
        pca_plot_svg = self.str_to_base64(res.rx2("pca_plot")[0])
        pca_eig = self.r2py(res.rx2("pca_eig"))
        pca_sample = self.r2py(res.rx2("pca_sample"))
        return {
            "meta": {"title": self.title},
            "plots": [
                {"format": "image/svg+xml;base64",
                    "title": "PCA Plot", "data": pca_plot_svg}
            ],
            "tables": {
                "pca_eig": pca_eig.to_dict(orient="records"),
                "pca_sample": pca_sample.to_dict(orient="records")
            }
        }
