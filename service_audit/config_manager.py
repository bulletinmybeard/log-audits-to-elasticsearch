import logging
import os
from typing import Optional, Any

import yaml
from pydantic import ValidationError

from service_audit.models import BaseConfig

logger = logging.getLogger("service_audit")


class ConfigManager:
    _config: Optional[BaseConfig] = None

    @classmethod
    def load_config(cls, config_file_path: str) -> Any:
        """
        Load and validate configuration from a YAML file.
        """
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(f"Config file not found: {config_file_path}")

        with open(config_file_path, "r") as f:
            raw_config = yaml.safe_load(f)

        try:
            cls._config = BaseConfig(**raw_config)
            logger.info("Configuration loaded successfully.")
            return cls._config
        except ValidationError as e:
            raise ValueError(f"Invalid configuration format: {e}")

    @classmethod
    def get_config(cls) -> BaseConfig:
        """
        Access the loaded configuration. Ensures configuration is loaded.
        """
        if cls._config is None:
            raise ValueError("Configuration has not been loaded.")
        return cls._config
