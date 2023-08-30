import logging

from concentrator.configs import create_configs
from concentrator.client import Client, TokenManager
from concentrator.logger import config_logger
from concentrator.lora import Lora
from concentrator.spaces import Spaces


logger = logging.getLogger(__name__)


def main():
    config_logger()
    configs = create_configs()
    client = Client(
        token_manager=TokenManager(
            configs.configs_dir.joinpath(configs.client.token_file)
        ),
        client_config=configs.client,
    )
    spaces = Spaces(
        client=client,
        spaces_file=configs.configs_dir.joinpath("spaces.json"),
    )
    lora = Lora(configs.lora)

    while True:
        message = lora.receive()
        if not (space := spaces.get(message.id)):
            continue
        client.update_space_state(space["id"], message.taken)
