from typing import Any, Dict

from backend.analysis.framework import BaseAnalysis, InputData, register_analysis, BaseModel


class TPMDownloadParams(BaseModel):
    pass


@register_analysis("tpm_download")
class TPMDownload(BaseAnalysis):
    title = "Tpm Data Download"
    Params = TPMDownloadParams
    input_type = InputData.tpm
    gene_filter: bool = True

    async def run(self) -> Dict[str, Any]:
        res = self.df
        return {
            "meta": {"title": self.title},
            "tables": {
                f"{TPMDownload.input_type}_data": res.to_dict(orient="records")
            }
        }
