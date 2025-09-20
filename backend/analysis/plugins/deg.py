from typing import Any, Dict
from pydantic import Field
from enum import Enum

from backend.analysis.framework import BaseAnalysis, BaseAnalysisParams, InputData, register_analysis
from backend.analysis.scripts.deg import deg_code  # 现有 R 脚本


class NORMALIZE(str, Enum):
    TMM: str = "TMM"
    RLE: str = "RLE"
    TMMwsp: str = "TMMwsp"
    upperquartile: str = "upperquartile"
    none: str = "none"


class DEGParams(BaseAnalysisParams):
    normalize_method: NORMALIZE = Field(
        default=NORMALIZE.TMM, description="Normalization method")
    fdr_threshold: float = Field(
        0.05, ge=0, le=1, description="FDR threshold for significance")
    log2fc_threshold: float = Field(
        1.0, ge=1.0, description="Log2 fold change threshold for significance")


@register_analysis("deg")
class DEGAnalysis(BaseAnalysis):
    title = "Differential Expression Analysis"
    input_type = InputData.counts
    Params = DEGParams

    async def run(self) -> Dict[str, Any]:
        res = await self.rproc.run_analysis(
            deg_code,
            expression_counts=self.rdata,
            width=self.params.width,
            height=self.params.height,
            normalize_method=self.params.normalize_method.value,
            fdr_threshold=self.params.fdr_threshold,
            log2fc_threshold=self.params.log2fc_threshold,
        )
        # 提取图像（每个对比一张 SVG）并转 base64
        plots_r = res.rx2("plots")
        plots_out = []
        for name in list(plots_r.names):
            svg_txt = str(plots_r.rx2(name)[0])
            plots_out.append({
                "format": "image/svg+xml;base64",
                "title": name,
                "data": self.str_to_base64(svg_txt),
            })

        # 表格：full 与 sig
        def rlist_to_records(rlist):
            out: Dict[str, list[dict[str, Any]]] = {}
            for name in list(rlist.names):
                df = self.r2py(rlist.rx2(name))
                out[name] = df.to_dict(orient="records")
            return out

        tables_full = rlist_to_records(res.rx2("tables"))
        tables_sig = rlist_to_records(res.rx2("sig_tables"))

        meta = {
            "title": self.title,
            "contrasts": list(res.rx2("meta").rx2("contrasts")),
            "fdr_cut": float(res.rx2("meta").rx2("fdr_cut")[0]),
            "lfc_cut": float(res.rx2("meta").rx2("lfc_cut")[0]),
            "normalize_method": str(res.rx2("meta").rx2("norm")[0]),
        }

        return {
            "meta": meta,
            "plots": plots_out,
            "tables": {"full": tables_full, "sig": tables_sig},
        }
