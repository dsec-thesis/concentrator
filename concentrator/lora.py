from LoRaRF import SX127x
import cbor2
from pydantic import BaseModel, ValidationError

from concentrator.configs import LoraAntennaConfig, LoraConfig, SpiConfig


class RxMessage(BaseModel):
    id: int
    taken: bool


class Lora:
    def __init__(self, configs: LoraConfig) -> None:
        self._configs = configs
        self._dev = self._init_dev(configs.spi)

    def _init_dev(self, configs: SpiConfig) -> SX127x:
        dev = SX127x()
        dev.begin(bus=configs.bus, cs=configs.chip_select, reset=configs.reset)
        return dev

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
        ack = cbor2.dumps({"id": id})
        self._dev.beginPacket()
        self._dev.write(ack, len(ack))
        self._dev.endPacket()
        self._dev.wait()

    def _wait(self) -> int:
        while True:
            self._dev.request()
            self._dev.wait()
            if not (length := self._dev.available()):
                continue
            if self._dev.status() == self._dev.STATUS_CRC_ERR:
                continue
            return length

    def receive(self) -> RxMessage:
        self._apply_antenna_configs(self._configs.rx)

        while True:
            print("waiting for message")
            length = self._wait()
            print("reading message")
            frame = self._dev.read(length)
            try:
                print("decoding message")
                raw_message = cbor2.loads(bytes(frame))
            except (cbor2.CBORDecodeError, UnicodeDecodeError):
                continue
            try:
                print("validating message")
                message = RxMessage.model_validate(raw_message)
            except ValidationError:
                continue

            print(message)
            print("sending ack")
            self._send_ack(message.id)
            return message
