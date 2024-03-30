import os
from typing import Optional

import yaml
from pydantic import ValidationError

from audit_logger.custom_logger import get_logger
from audit_logger.models import AppConfig

logger = get_logger("audit_service")


class ConfigManager:
    _config: Optional[AppConfig] = None

    @classmethod
    def load_config(cls, config_file_path: str) -> AppConfig:
        """
        Load and validate configuration from a YAML file.
        """
        if not os.path.exists(config_file_path):
            raise FileNotFoundError("Config file not found: %s", config_file_path)

        with open(config_file_path, "r") as f:
            raw_config = yaml.safe_load(f)

        try:
            cls._config = AppConfig(**raw_config)
            logger.info("App configuration loaded.")
            return cls._config
        except ValidationError as e:
            raise ValueError("Invalid app configuration format: %s", e)

    @classmethod
    def get_config(cls) -> AppConfig:
        """
        Access the loaded configuration. Ensures configuration is loaded.
        """
        if cls._config is None:
            raise ValueError("Configuration has not been loaded.")
        return cls._config
