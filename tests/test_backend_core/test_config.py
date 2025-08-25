import yaml
import pytest
from backend.api.config import Config
from pathlib import Path


@pytest.fixture
def sample_yaml(tmp_path: Path) -> tuple[Path, dict]:
    config_data = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "user": "testuser"
        },
        "debug": True,
        "api_key": "secret"
    }
    config_file = tmp_path / "test_config.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(config_data, f)
    return config_file, config_data


def test_config_attribute_access(sample_yaml):
    config_file, config_data = sample_yaml
    config = Config(str(config_file))
    assert config.debug == config_data["debug"]
    assert config.api_key == config_data["api_key"]


def test_config_nested_access(sample_yaml):
    config_file, config_data = sample_yaml
    config = Config(str(config_file))
    assert config.database.host == config_data["database"]["host"]
    assert config.database.port == config_data["database"]["port"]
    assert config.database.user == config_data["database"]["user"]


def test_config_missing_key_raises(sample_yaml):
    config_file, _ = sample_yaml
    config = Config(str(config_file))
    with pytest.raises(AttributeError):
        _ = config.nonexistent


def test_config_nested_missing_key_raises(sample_yaml):
    config_file, _ = sample_yaml
    config = Config(str(config_file))
    with pytest.raises(AttributeError):
        _ = config.database.nonexistent
