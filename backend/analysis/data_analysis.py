from abc import ABC, abstractmethod
import rpy2.robjects as ro
from rpy2.rinterface_lib.embedded import RRuntimeError
from multiprocessing import Pool
import asyncio
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class DataAnalysis(ABC):
    """Base class for data analysis tasks."""

    @abstractmethod
    def run_analysis(self):
        """Run the data analysis."""
        pass


class RProcessor(DataAnalysis):

    def __init__(self, pool_size=4):
        self.pool_size = pool_size
        self.pool = None
        self._initialize_pool()

    def _initialize_pool(self):
        """
        Initialize a process pool for R tasks.
        """
        self.pool = Pool(processes=self.pool_size, initializer=self._init_r)
        logger.info(f"Initialized process pool with {self.pool_size} workers")

    @staticmethod
    def _init_r():
        """
        Initialize a tidyverse R environment in each worker process.
        """
        try:
            ro.r("""
                 suppressPackageStartupMessages(library(tidyverse))
                 suppressPackageStartupMessages(library(Cairo))
                 """)
            logger.debug("R environment initialized in process")
        except Exception as e:
            logger.error(f"Failed to initialize R: {str(e)}")

    @staticmethod
    @contextmanager
    def _isolated_r_environment():
        """
        Create an isolated R environment for each task.
        This ensures that each task runs in a clean R environment.
        """
        original_env = ro.globalenv.copy()
        try:
            new_env = ro.Environment()
            ro.r.setenv(new_env)
            yield new_env
        finally:
            ro.r.setenv(original_env)
            ro.r('rm(list=ls())')
            logger.debug("R environment cleaned up")

    def run_analysis(self, r_code: str, **kwargs) -> ro.RObject:
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
            with self._isolated_r_environment():
                for key, value in kwargs.items():
                    ro.globalenv[key] = value
                result = ro.r(r_code)
                return result
        except RRuntimeError as e:
            logger.error(f"R runtime error: {str(e)}")
            raise Exception(f"R error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in R task: {str(e)}")

    async def async_run_analysis(self, r_code: str, **kwargs) -> ro.RObject:
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
        loop = asyncio.get_event_loop()
        for attempt in range(2):
            try:
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: self.pool.apply(
                        self.run_analysis, (r_code,), kwargs)),
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
            self.pool.close()
            self.pool.join()
            logger.info("Process pool closed")
            self.pool = None
