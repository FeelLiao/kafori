import redis.asyncio as redis
from redis.asyncio.sentinel import Sentinel
from redis.asyncio.cluster import RedisCluster
from redis.cluster import ClusterNode

from .config import settings
import logging

logger = logging.getLogger(__name__)


def build_redis_pool():
    cfg = settings.redis
    kwargs = {
        "db": cfg.db,
        "password": cfg.password or None,
        "decode_responses": False,
        "max_connections": cfg.max_connections,
    }

    if cfg.mode == "single":
        return redis.Redis(host=cfg.host, port=cfg.port, **kwargs)

    if cfg.mode == "sentinel":
        sentinels = [tuple(n.split(":")) for n in cfg.sentinel_nodes]
        sentinel = Sentinel(sentinels, **kwargs)
        return sentinel.master_for(cfg.sentinel_name, **kwargs)

    if cfg.mode == "cluster":
        nodes = [
            ClusterNode(host=h, port=int(p))
            for node in cfg.cluster_nodes
            for h, p in [node.split(":")]
        ]
        return RedisCluster(startup_nodes=nodes, **kwargs)

    raise ValueError(f"Unsupported redis mode: {cfg.mode}")
