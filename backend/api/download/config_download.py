from pathlib import Path
from backend.api.dl_providers import BaseDownload, register_download

REPO_ROOT = Path(__file__).resolve().parents[2]


@register_download("genome")
class GenomeDownload(BaseDownload):

    def catalog(self):
        return {
            "filename": "genome.fa.gz",
            "media_type": "application/gzip"
        }

    def response(self):
        pass
