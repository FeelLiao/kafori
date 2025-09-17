# Cache.py
import hashlib
import json,pickle
import functools
from typing import Callable, Any, Optional
from .Redis import get_conn   # 全局单例

def _make_key(*args, **kwargs) -> str:
    # 1) 只保留“业务维度”字段；可按需要扩展
    # 2) 用 json.dumps 保证顺序一致，跨进程一致
    # 3) 用 MD5 缩短长度，仍可人工阅读
    content = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(content.encode()).hexdigest()[:16]

def cache(
        expire: int = 60,
        key_prefix: str = "",
        key: Optional[str] = None
):
    """
     通用的redis缓存装饰器，用于数据缓存，减轻请求处理
     Args:
        expire: 存活时间(秒)
        key_prefix: 键前缀
        key: 自定义键(可选)
     Returns:
        decorator redis数据缓存的结果
     """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            redis = get_conn()

            # 1) 生成 cache_key
            if key:
                cache_key = f"{key}:{_make_key(*args, **kwargs)}"
            else:
                cache_key = f"{key_prefix}:{func.__name__}:{_make_key(*args, **kwargs)}"

            # 2) 缓存逻辑
            data = await redis.get(cache_key)
            if data is not None:
                print(pickle.loads(data))
                return pickle.loads(data)

            result = await func(*args, **kwargs)
            await redis.set(cache_key, pickle.dumps(result), ex=expire)
            return result
        return wrapper
    return decorator