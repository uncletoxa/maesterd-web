from pydantic import ValidationError
from typing import Any
from pydantic import BaseModel, Field


class GraphParamsConfig(BaseModel):
    debug: bool = Field(False, description="debug mode")
    recursion_limit: int = Field(300, description="recursion limit")


class CampaignConfig(BaseModel):
    numpc: int = Field(4, description="number of playable characters")


class ConfigSets(BaseModel):
    graph: GraphParamsConfig = Field(default=GraphParamsConfig())
    campaign: CampaignConfig = Field(default=CampaignConfig())


class ConfigEntry(BaseModel):
    maesterd: ConfigSets = Field(default=ConfigSets())


class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._config = ConfigEntry(
                maesterd=ConfigSets(params=GraphParamsConfig(), campaign=CampaignConfig())
            )
        return cls._instance

    def set(self, key: str, value: Any):
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            config = getattr(config, k)
        setattr(config, keys[-1], value)

    def get(self, key: str, default=None):
        keys = key.split(".")
        config = self._config
        for k in keys:
            config = getattr(config, k, default)
        return config

    def dict(self):
        return self._config.dict()

    def validate(self):
        try:
            self._config = ConfigEntry.parse_obj(self._config.dict())  # noqa
        except ValidationError as e:
            print(e)
