import json
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class LoraAntennaConfig(BaseModel):
    frequency: int
    spreading_factor: int
    bandwidth: int
    coding_rate: int
    preamble_length: int
    crc_enable: bool
    sync_word: int


class SpiConfig(BaseModel):
    bus: int
    chip_select: int
    reset: int


class LoraConfig(BaseModel):
    rx: LoraAntennaConfig
    tx: LoraAntennaConfig
    spi: SpiConfig


class ClientConfig(BaseModel):
    client_id: str
    client_secret: str
    token_url: str
    token_file: str
    api_url: str
    parkinglot_id: str


class ConcentratorConfig(BaseSettings):
    configs_dir: Path
    lora: LoraConfig
    client: ClientConfig


def create_configs() -> ConcentratorConfig:
    configs_dir = Path.home().joinpath(".config/concentrator")
    with configs_dir.joinpath("config.json").open("r") as f:
        return ConcentratorConfig.model_validate(
            {**json.load(f), "configs_dir": configs_dir}
        )


if __name__ == "__main__":
    print(create_configs().model_dump())
