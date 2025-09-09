from abc import ABC, abstractmethod
import rpy2.robjects as ro
from rpy2.rinterface_lib.embedded import RRuntimeError
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor
import asyncio
from contextlib import contextmanager
import logging
import functools
import os

logger = logging.getLogger(__name__)


class DataAnalysis(ABC):
    """Base class for data analysis tasks."""

    @abstractmethod
    def run_analysis(self):
        """Run the data analysis."""
        pass


@contextmanager
def isolated_r_environment():
    """
    Create an isolated R environment for each task.
    This ensures that each task runs in a clean R environment.
    """
    try:
        new_env = ro.globalenv
        yield new_env
    finally:
        ro.r('rm(list=ls())')
        logger.info("R environment cleaned up")


def run_analysis(r_code: str, kwargs: dict) -> ro.RObject:
    """
    run the R analysis code with the provided arguments.
    Args:
        r_code: R code to execute.
        kwargs: Arguments to pass to the R code.
    Returns:
        RObject (rpy2.robjects): Result of the R code execution.
    Raises:
        Exception: If there is an error during R code execution.
    """
    try:
        with isolated_r_environment():
            for key, value in kwargs.items():
                ro.globalenv[key] = value
            result = ro.r(r_code)
            return result
    except RRuntimeError as e:
        logger.error(f"R runtime error: {str(e)}")
        raise Exception(f"R error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in R task: {str(e)}")


class RProcessorPoolMP(DataAnalysis):
    """Processor for running R code in a separate process pool.
    This class initialize `pool_size` R environment when you create an instance
    and provides methods to run R code asynchronously. You need to call `close()`
    method to clean up the resources.
    Attributes:
        pool_size (int): Number of worker processes in the pool.
    """

    def __init__(self, pool_maxsize=1):
        self.pool = None
        self.max_pool_size: int = max(pool_maxsize, os.cpu_count(), 2)
        self._initialize_pool()

    def _initialize_pool(self):
        """
        Initialize a process pool for R tasks.
        """

        self.pool = Pool(processes=self.max_pool_size,
                         initializer=self._init_r)
        logger.info(
            f"Initialized process pool with {self.max_pool_size} workers")

    @staticmethod
    def _init_r():
        """
        Initialize a tidyverse R environment in each worker process.
        """
        try:
            ro.r("""
                suppressPackageStartupMessages(library(tidyverse))
                suppressPackageStartupMessages(library(svglite))

                plot_to_raw <- function(plot_obj, width=800, height=600) {
                tf <- tempfile(fileext = ".svg")
                svglite(file = tf, width = width /72 , height = height /72)
                print(plot_obj)
                dev.off()
                img_raw <- readChar(tf, nchars=file.info(tf)$size, useBytes=TRUE)
                unlink(tf)
                return(img_raw)
              }
                 """)
            logger.info("R environment initialized in process")
        except Exception as e:
            logger.error(f"Failed to initialize R: {str(e)}")

    async def run_analysis(self, r_code: str, **kwargs) -> ro.RObject:
        """
        Asynchronously run the R analysis code with the provided arguments.
        The result should be a list with named elements in R.
        When accessing the result, use `result.rx2('name')` to get the specific element.
        Args:
            r_code: R code to execute.
            kwargs: Arguments to pass to the R code.
        Returns:
            RObject (rpy2.robjects): Result of the R code execution.
        Raises:
            Exception: If there is an error during R code execution.
        """
        loop = asyncio.get_running_loop()
        for attempt in range(2):
            try:
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: self.pool.apply(
                        run_analysis, (r_code, kwargs))),
                    timeout=60
                )
                return result
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1} in 60s")
                continue
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
                continue
        raise Exception("Failed after 2 attempts")

    def close(self):
        """
        Close the RProcessor and its process pool.
        """
        if self.pool:
            # stop accepting new tasks
            self.pool.close()
            # wait for the worker processes to finish
            self.pool.join()
            logger.info("Process pool closed")
            # reset the pool to None
            self.pool = None


class RProcessorPoolCPPE(RProcessorPoolMP):
    """Processor for running R code in a separate process pool.
    This class initialize a R environment when you submit a task
    and provides methods to run R code asynchronously.
    Attributes:
        pool_maxsize (int): Max number of worker processes in the pool.
    """

    def __init__(self, pool_maxsize=4):
        self.max_pool_size: int = min(pool_maxsize, os.cpu_count(), 2)
        self.executor = None
        self._initialize_executor()

    def _initialize_executor(self):
        """
        Initialize a process pool for R tasks.
        """
        self.executor = ProcessPoolExecutor(
            max_workers=self.max_pool_size, initializer=self._init_r)
        logger.info("Initialized R process pool executor")

    async def run_analysis(self, r_code: str, **kwargs) -> ro.RObject:
        loop = asyncio.get_running_loop()
        for attempt in range(2):
            try:
                func = functools.partial(run_analysis, r_code, kwargs)
                result = await asyncio.wait_for(
                    loop.run_in_executor(self.executor, func),
                    timeout=60
                )
                return result
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1} in 60s")
                continue
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
                continue
        raise Exception("Failed after 2 attempts")

    def close(self):
        if self.executor:
            self.executor.shutdown(wait=True)
            logger.info("Process pool executor closed")
            self.executor = None
