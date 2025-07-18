
import logging
from abc import ABC, abstractmethod


class DataAnalysis(ABC):
    """Base class for data analysis tasks."""
    def __init__(self):
        self.logger = self._setup_logger()
        self._check_paths()

    def _setup_logger(self):
        """Set up a logger for the data analysis."""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    @abstractmethod
    def run_analysis(self):
        """Run the data analysis."""
        pass

    def log(self, message):
        self.logger.info(message)
