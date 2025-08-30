from pydantic import BaseModel, Field
import yaml
from typing import List


class MysqlConf(BaseModel):
    host: str = "127.0.0.1"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "test"
    charset: str = "utf8mb4"
    pool_size: int = 10
    max_pool_size: int = 50
    max_overflow: int = 10
    pool_recycle: int = 3600
    echo: bool = False


class RedisConf(BaseModel):
    mode: str = Field("single", pattern=r"single|sentinel|cluster")
    host: str = "127.0.0.1"
    port: int = 6379
    db: int = 0
    password: str = ""
    max_connections: int = 50
    sentinel_nodes: List[str] = []
    sentinel_name: str = "mymaster"
    cluster_nodes: List[str] = []


class Settings(BaseModel):
    mysql: MysqlConf = MysqlConf()
    redis: RedisConf = RedisConf()

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, "r", encoding="utf-8") as f:
            return cls(**yaml.safe_load(f))


settings = Settings.from_yaml("backend/conf/settings.yaml")
