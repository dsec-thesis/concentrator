import logging
from typing import Optional

from LoRaRF import SX127x
import cbor2
from pydantic import BaseModel, ValidationError

from concentrator.configs import LoraAntennaConfig, LoraConfig, SpiConfig

logger = logging.getLogger(__name__)


class LoraInitError(Exception):
    pass


class RxMessage(BaseModel):
    id: int
    taken: bool


class Lora:
    def __init__(self, configs: LoraConfig) -> None:
        self._configs = configs
        self._init()

    def receive(self) -> RxMessage:
        self._apply_antenna_configs(self._configs.rx)
        while True:
            length = self._wait()
            logger.debug(f"received message len {length}")
            if not (message := self._process_received_message(length)):
                continue
            logger.debug("valid message received")
            self._send_ack(message.id)
            logger.debug("ack sent")
            return message

    def _init(self) -> None:
        spi = self._configs.spi
        self._dev = SX127x()
        if not self._dev.begin(bus=spi.bus, cs=spi.chip_select, reset=spi.reset):
            raise LoraInitError

    def _apply_antenna_configs(self, configs: LoraAntennaConfig):
        self._dev.setModem(self._dev.LORA_MODEM)
        self._dev.setFrequency(configs.frequency)
        self._dev.setSpreadingFactor(configs.spreading_factor)
        self._dev.setBandwidth(configs.bandwidth)
        self._dev.setCodeRate(configs.coding_rate)
        self._dev.setHeaderType(self._dev.HEADER_EXPLICIT)
        self._dev.setPreambleLength(configs.preamble_length)
        self._dev.setCrcEnable(configs.crc_enable)
        self._dev.setSyncWord(configs.sync_word)

    def _send_ack(self, id: int) -> None:
        self._apply_antenna_configs(self._configs.tx)
        self._dev.beginPacket()
        self._dev.write(id)
        self._dev.endPacket()
        self._dev.wait()

    def _wait(self) -> int:
        while True:
            self._dev.request()
            self._dev.wait()
            if not (length := self._dev.available()):
                continue
            if self._dev.status() == self._dev.STATUS_CRC_ERR:
                logger.error("received message with crc error")
                continue
            return length

    def _process_received_message(self, length: int) -> Optional[RxMessage]:
        message_bytes = bytes(self._dev.read(length))
        try:
            raw_message = cbor2.loads(message_bytes)
        except (cbor2.CBORDecodeError, UnicodeDecodeError) as error:
            logger.error(f"cbor decode error {error}")
            return None
        try:
            message = RxMessage.model_validate(raw_message)
        except ValidationError as error:
            logger.error(f"error validating model {error}")
            return None
        return message
