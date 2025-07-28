import yaml


class Config:
    def __init__(self, config_path: str):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format in {config_path}: {e}")

    def __getattr__(self, key):
        if key not in self._config:
            raise AttributeError(f"Config has no attribute '{key}'")
        value = self._config[key]
        if isinstance(value, dict):
            return Config._from_dict(value)  # 使用类方法处理嵌套字典
        return value

    @classmethod
    def _from_dict(cls, config_data: dict):
        """Helper method to create Config from a dictionary."""
        instance = cls.__new__(cls)
        instance._config = config_data
        return instance


config = Config("backend/settings.yaml")
