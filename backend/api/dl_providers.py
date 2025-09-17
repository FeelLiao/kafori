import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Type, Optional
import mimetypes
import threading

from fastapi.responses import FileResponse, StreamingResponse

logger = logging.getLogger(__name__)


class BaseDownload(ABC):
    """
    统一下载项基类：
    - classes: 数据类别
    - items: 数据相字典， 如 {"raw": ..., "processed": ...}
    """
    classes: str = "misc"
    items: Dict[str, Any] = {}
    _items_ready: bool = False
    _items_lock: threading.Lock = threading.Lock()

    def __init_subclass__(cls, **kwargs):
        # 为每个子类分配独立缓存与锁，避免跨类阻塞/污染
        super().__init_subclass__(**kwargs)
        cls.items = {}
        cls._items_ready = False
        cls._items_lock = threading.RLock()

    def __init__(self):
        self._ensure_items_loaded()

    def _ensure_items_loaded(self):
        cls = self.__class__
        if getattr(cls, "_items_ready", False):
            return
        # 先计算，后上锁，减少锁持有时间（允许并发重复计算，最后一次赋值即可）
        items = self.catalog() or {}
        if not isinstance(items, dict):
            raise ValueError(f"{cls.__name__}.catalog() must return dict")
        with cls._items_lock:
            if getattr(cls, "_items_ready", False):
                return
            cls.items = items
            cls._items_ready = True

    @classmethod
    def refresh_items(cls):
        # 先计算，后切换，且避免走 __init__ 以防再次加锁
        inst = object.__new__(cls)  # 跳过 __init__，避免递归加锁
        items = cls.catalog(inst) or {}
        if not isinstance(items, dict):
            raise ValueError(f"{cls.__name__}.catalog() must return dict")
        with cls._items_lock:
            cls.items = items
            cls._items_ready = True

    @abstractmethod
    def catalog(self) -> Dict[str, Any]:
        """
        返回：
          {
            "filename": "xxx.ext",
            "media_type": "text/plain"
          }
        """
        raise NotImplementedError

    @abstractmethod
    def response(self) -> FileResponse | StreamingResponse:
        raise NotImplementedError

    @staticmethod
    def file_payload(path: Path, filename: Optional[str] = None, media_type: Optional[str] = None) -> Dict[str, Any]:
        p = Path(path).resolve()
        if not p.is_file():
            raise FileNotFoundError(f"File not found: {p}")
        return {
            "filename": filename or p.name,
            "media_type": media_type or (mimetypes.guess_type(str(p))[0] or "application/octet-stream"),
            "path": str(p),
        }


_registry: Dict[str, Type[BaseDownload]] = {}


def register_download(classes_: str):
    """
    装饰器：注册下载提供者
    """
    def _decorator(cls: Type[BaseDownload]):
        cls.classes = classes_
        _registry[classes_] = cls
        return cls
    return _decorator


def handle_download(classes_: str) -> Type[BaseDownload]:
    if classes_ not in _registry:
        raise KeyError(f"Unknown analysis: {classes_}")
    return _registry[classes_]


def get_catalog() -> list[dict[str, Any]]:
    items = []
    for k, cls in _registry.items():
        try:
            cls.refresh_items() if not getattr(cls, "_items_ready", False) else None
        except Exception as e:
            logger.error(f"Error refreshing items for {cls.__name__}: {e}")
        items.append({
            "classes": cls.classes,
            "items": cls.items,
        })
    return items
