import logging
import time

from concentrator.configs import create_configs
from concentrator.logger import config_logger
from concentrator.lora import Lora


logger = logging.getLogger(__name__)

RESTUL_TEMPLATE = """

Results
Number of messages processed:   {processed_messages} messages
Elapsed time:                   {elapsed_time:.2f} seconds
Messages per second:            {processed_messages_per_second:.2f} messages/second

"""


def main():
    config_logger(logging.INFO)
    logger.info("initializing load test")
    configs = create_configs()
    lora = Lora(configs.lora)

    logger.info("start")
    start, processed_messages = time.time(), 0
    try:
        while True:
            lora.receive()
            processed_messages += 1

    except KeyboardInterrupt:
        pass

    elapsed_time = time.time() - start
    processed_messages_per_second = processed_messages / elapsed_time
    print(
        RESTUL_TEMPLATE.format(
            processed_messages=processed_messages,
            elapsed_time=elapsed_time,
            processed_messages_per_second=processed_messages_per_second,
        )
    )


if __name__ == "__main__":
    main()
