from typing import Any, Dict

from backend.analysis.framework import BaseAnalysis, InputData, register_analysis, BaseModel


class CountsDownloadParams(BaseModel):
    pass


@register_analysis("counts_download")
class CountsDownload(BaseAnalysis):
    title = "Counts Data Download"
    Params = CountsDownloadParams
    input_type = InputData.counts
    gene_filter: bool = True

    async def run(self) -> Dict[str, Any]:
        res = self.df
        return {
            "meta": {"title": self.title},
            "tables": {
                f"{CountsDownload.input_type}_data": res.to_dict(orient="records")
            }
        }
