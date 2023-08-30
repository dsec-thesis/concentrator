import logging

from concentrator.configs import create_configs
from concentrator.client import Client, TokenManager
from concentrator.logger import config_logger
from concentrator.lora import Lora
from concentrator.spaces import Spaces


logger = logging.getLogger(__name__)


def main():
    config_logger()
    logger.info("initializing concentrator")
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

    logger.info("ready for receiving messages")
    while True:
        message = lora.receive()
        logger.info(f"new message {message}")
        if not (space := spaces.get(message.id)):
            logger.error(f"space not found, space id: {message.id}")
            continue
        logger.info(f"updating space {space['id']}")
        client.update_space_state(space["id"], message.taken)
