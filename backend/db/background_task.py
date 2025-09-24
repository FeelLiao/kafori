import asyncio
import json
import logging
from typing import Any, List, Dict
import pandas as pd

from backend.db.interface import GetDataBaseInterface
from backend.api.config import config

db = GetDataBaseInterface()

logger = logging.getLogger(__name__)

DEFAULT_INTERVAL_SECONDS = float(
    config.interval_refresh_hours) * 60 * 60  # 12h


async def refresh_stat_cache(redis) -> List[Dict[str, Any]]:
    """
    刷新统计信息缓存。
    """

    logger.info("Refreshing statistic information cache...")

    payload = await db.get_data_static()
    # 统计逻辑
    payload_new = payload[["SampleID", "CollectionTime", "SampleAge",
                           "CollectionPart", "Experiment", "ExperimentCategory"]]

    logger.info("Fetched %d records from database for statistics",
                len(payload_new))

    payload_new = payload.loc[:, ["SampleID", "CollectionTime", "SampleAge",
                                  "CollectionPart", "Experiment", "ExperimentCategory"]].copy()
    payload_new["CollectionTime"] = pd.to_datetime(
        payload_new["CollectionTime"], errors="coerce")  # 如有固定格式加 format="..."
    payload_new["SampleID"] = payload_new["SampleID"].astype("string")
    payload_new["CollectionPart"] = payload_new["CollectionPart"].astype(
        "category")
    payload_new["Experiment"] = payload_new["Experiment"].astype("category")
    payload_new["ExperimentCategory"] = payload_new["ExperimentCategory"].astype(
        "category")

    logger.info(
        "Statistics information dataframe has been assigned right data types.")
    exp_counts = (payload_new.groupby(["ExperimentCategory", "Experiment"], observed=True)
                  .size()
                  .reset_index(name="count")
                  .sort_values(["ExperimentCategory", "count"], ascending=[True, False])).head(10)
    year_counts = (
        payload_new["CollectionTime"].dt.year
        .dropna()
        .value_counts()
        .sort_index()
        .rename_axis("Year")
        .reset_index(name="count")
    ).head(10)
    res = {
        "exp_counts": exp_counts.to_dict(orient="records"),
        "year_counts": year_counts.to_dict(orient="records"),
    }
    logger.info("Statistics computed: %d experiment counts, %d year counts",
                len(exp_counts), len(year_counts))

    await redis.set("transcripts_stats:exp_counts", json.dumps(res["exp_counts"]))
    logger.info("transcripts_stats:exp_counts cache refreshed, items=%d",
                len(exp_counts))
    await redis.set("transcripts_stats:year_counts", json.dumps(res["year_counts"]))
    logger.info("transcripts_stats:year_counts cache refreshed, items=%d",
                len(year_counts))
    return 0


async def start_periodic_refresh(app, interval_seconds: int = DEFAULT_INTERVAL_SECONDS):
    """
    应用启动后调用：周期性刷新缓存。
    """
    # 等待 Redis 就绪（最多等待 60 秒）
    for i in range(60):
        redis = getattr(app.state, "redis", None)
        if redis:
            break
        await asyncio.sleep(1)
    else:
        logger.error(
            "Redis not available in app.state.redis; periodic refresh not started.")
        return

    logger.info("Starting periodic stat cache refresh every %ss",
                interval_seconds)
    while True:
        try:
            await refresh_stat_cache(app.state.redis)
        except Exception as e:
            logger.exception("Periodic stat cache refresh failed: %s", e)
        await asyncio.sleep(interval_seconds)
