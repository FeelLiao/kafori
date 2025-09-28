from abc import ABC, abstractmethod
import rpy2.robjects as ro
from rpy2.rinterface_lib.embedded import RRuntimeError
# from multiprocessing import Pool  # 不再需要
from concurrent.futures import ProcessPoolExecutor
import asyncio
from contextlib import contextmanager
import logging
import functools
import warnings

logger = logging.getLogger(__name__)

R_INIT_CODE = """
  suppressPackageStartupMessages(library(tidyverse))
  suppressPackageStartupMessages(library(svglite))
  plot_to_raw <- function(plot_obj, width=800, height=600) {
    tf <- tempfile(fileext = ".svg")
    svglite(file = tf, width = width/72, height = height/72)
    print(plot_obj); dev.off()
    img_raw <- readChar(tf, nchars=file.info(tf)$size, useBytes=TRUE)
    unlink(tf); img_raw
  }
"""


class DataAnalysis(ABC):
    @abstractmethod
    def run_analysis(self):
        pass


@contextmanager
def isolated_r_environment():
    try:
        new_env = ro.globalenv
        yield new_env
    finally:
        ro.r('rm(list=ls())')
        logger.debug("R environment cleaned up")


def _task_runner(r_code: str, kwargs: dict, init_each_time: bool) -> ro.RObject:
    try:
        with isolated_r_environment():
            if init_each_time:
                # 幂等初始化（第二次以后极快）
                ro.r(R_INIT_CODE)
            for k, v in kwargs.items():
                ro.globalenv[k] = v
            return ro.r(r_code)
    except RRuntimeError as e:
        raise Exception(f"R error: {e}")
    except Exception:
        raise


class RProcessorPoolBase(DataAnalysis):
    """
    统一的 R 进程池执行器（基于 ProcessPoolExecutor）。
    兼容旧接口 run_analysis(r_code, **kwargs)。
    """

    def __init__(self, pool_maxsize: int = 2, timeout: int = 60, retries: int = 1, init_each_time: bool = True):
        self.max_pool_size = pool_maxsize
        self.timeout = timeout
        self.retries = retries
        self.init_each_time = init_each_time
        self.executor: ProcessPoolExecutor | None = None
        self._initialize_executor()

    def _initialize_executor(self):
        self.executor = ProcessPoolExecutor(
            max_workers=self.max_pool_size,
            # initializer=self._process_level_init
        )
        logger.info(f"Initialized R executor with {self.max_pool_size} workers")

    @staticmethod
    def _process_level_init():
        # 进程级预热（可选：这里也执行一次，降低首个任务延迟）
        try:
            ro.r()
            logger.info("R process-level init done")
        except Exception as e:
            logger.error(f"Process-level R init failed: {e}")

    async def run_analysis(self, r_code: str, **kwargs) -> ro.RObject:
        if not self.executor:
            raise RuntimeError("Executor not initialized or already closed.")
        loop = asyncio.get_running_loop()
        last_exc = None
        for attempt in range(1, self.retries + 1):
            try:
                func = functools.partial(_task_runner, r_code, kwargs, self.init_each_time)
                result = await asyncio.wait_for(
                    loop.run_in_executor(self.executor, func),
                    timeout=self.timeout
                )
                return result
            except asyncio.TimeoutError as e:
                last_exc = e
                logger.warning(f"R task timeout (attempt {attempt}/{self.retries}, {self.timeout}s)")
            except Exception as e:
                last_exc = e
                logger.error(f"R task error (attempt {attempt}/{self.retries}): {e}")
        raise Exception(f"R task failed after {self.retries} attempts: {last_exc}")

    def close(self):
        if self.executor:
            self.executor.shutdown(wait=True)
            logger.info("R executor closed")
            self.executor = None


# 兼容旧类名：保留并发出弃用警告
class RProcessorPoolCPPE(RProcessorPoolBase):
    pass


class RProcessorPoolMP(RProcessorPoolBase):
    def __init__(self, *a, **kw):
        warnings.warn(
            "RProcessorPoolMP is deprecated; using unified ProcessPool implementation.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*a, **kw)
