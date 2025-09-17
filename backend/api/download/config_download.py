import mimetypes
from pathlib import Path
from fastapi.responses import FileResponse

from backend.api.dl_providers import BaseDownload, register_download
from backend.api.config import config
import logging


logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parents[3]


@register_download("genomic_data")
class GenomeDownload(BaseDownload):
    """
    Download genomic data implementation class.
    """

    download_dict: dict[str, dict[str, str]] = {}

    def config_phase(self) -> dict[str, dict[str, str]]:
        """
        Phase configuration to dict for genomic data download.
        """
        try:
            dl = getattr(config, "download")
        except AttributeError:
            logger.warning("Download value in configuration not found.")
            return {}

        # 提取底层 dict
        if hasattr(dl, "_config"):
            dl_dict = dl._config  # Config 对象包装的底层字典
        elif isinstance(dl, dict):
            dl_dict = dl
        else:
            logger.warning("Download value in configuration is not valid, setting to empty dict.")
            return {}

        items = {}
        for name, rel in dl_dict.items():
            p = Path(rel)
            p = (REPO_ROOT / p).resolve() if not p.is_absolute() else p.resolve()
            media = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
            items[name] = {
                "filename": p.name,
                "media_type": media,
                "path": str(p),
            }
        return items

    def catalog(self) -> dict[str, dict[str, str]]:
        raw = self.config_phase() or {}
        self.__class__.download_dict = raw
        # 去掉 path 字段
        return {
            k: {kk: vv for kk, vv in meta.items() if kk != "path"}
            for k, meta in raw.items()
        }

    def response(self, filename: str) -> FileResponse:
        raw = getattr(self.__class__, "download_dict", None) or (self.config_phase() or {})
        if not getattr(self.__class__, "download_dict", None):
            self.__class__.download_dict = raw

        for _, meta in raw.items():
            if meta.get("filename") == filename:
                p = Path(meta["path"])
                if not p.is_file():
                    raise FileNotFoundError(f"File not found: {p}")
                media = meta.get("media_type")
                return FileResponse(path=str(p), filename=filename, media_type=media)
        raise FileNotFoundError(f"Unknown filename: {filename}")