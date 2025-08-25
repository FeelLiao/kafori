import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Config:
    def __init__(self, config: str):
        config_path = Path(config)
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path.absolute()}")
            raise FileNotFoundError(f"Config file not found: {config_path.absolute()}")
        except yaml.YAMLError as e:
            logger.error(f"Invalid yaml format detected for {config_path.absolute()}")
            raise ValueError(f"Invalid YAML format in {config_path.absolute()}: {e}")

    def __getattr__(self, key):
        if key not in self._config:
            raise AttributeError(f"Config has no attribute '{key}'")
        value = self._config[key]
        if isinstance(value, dict):
            # Recursively convert dicts to Config objects
            return Config._from_dict(value)
        return value

    @classmethod
    def _from_dict(cls, config_data: dict):
        """Helper method to create Config from a dictionary."""
        instance = cls.__new__(cls)
        instance._config = config_data
        return instance


config = Config("backend/settings.yaml")
logger.info("Configuration loaded successfully.")
