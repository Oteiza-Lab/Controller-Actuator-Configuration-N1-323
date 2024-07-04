import logging
from typing import Optional
import serial
import time

PORT = 'COM3'

class CopMotorError(Exception):
    pass

class CopMotor:

    def __init__(self, port) -> None:
        self._dev = serial.Serial(timeout=15)  # 15 second timeout
        self._scale_factor = 0.00625
        if port is not None:
            self._dev.port = port
            self.open()
        else:
            self._port = ''

    def _log_str(self, data) -> str:
        return data

    def open(self) -> None:
        self._dev.open()

    def write(self, data: str) -> None:
        logging.debug('write: %s', data)
        self._dev.write(data.encode() + b'\r')

    def read(self) -> str:
        data = self._dev.read_until(b'\r').decode()[:-1]
        logging.debug('read: %s', data)
        return data

    def set(self, data: str) -> None:
        self.write('s ' + data)
        if self.read() != 'ok':
            raise CopMotorError

    def get(self, data: str):
        self.write('g '+ data)
        data = self.read()
        if data[0] == 'v':
            return data.split(' ')[1]
        raise CopMotorError

    def trajectory(self) -> None:
        self.write('t 1')
        if self.read() != 'ok':
            raise CopMotorError

    def set_mode_relative_move(self):
        #logging.info(self._log_str("set mode relative move"))
        self.set('r0xC8 256')

    def set_mode_programmed_position(self):
        #logging.info(self._log_str("set mode programmed position"))
        self.set('r0xC4 21')

    def set_relative_move(self, data):
        x = int(data / self._scale_factor)
        #logging.info(self._log_str(f"set relative move: {x}"))
        self.set(f"r0xCA {x}")

    def set_profile_velocity(self, data: float):
        x = int(data / self._scale_factor)
        #logging.info(self._log_str(f"set profile velocity: {x}"))
        self.set(f"r0xcb {x}")

    def set_profile_acceleration(self, data: float):
        x = int(data / self._scale_factor)
        #logging.info(self._log_str(f"set profile acceleration: {x}"))
        self.set(f"r0xcc {x}")

    def set_profile_deceleration(self, data: float):
        x = int(data / self._scale_factor)
        #logging.info(self._log_str(f"set profile deceleration: {x}"))
        self.set(f"r0xcd {x}")

    def get_motor_position(self) -> float:
        data = float(self.get('r0x32')) * self._scale_factor
        logging.info(self._log_str(f" Motor position: {data}"))
        return data

    def get_load_position(self) -> float:
        data = float(self.get('r0x17')) * self._scale_factor
        #logging.info(self._log_str(f"load position: {data}"))

    def get_following_error(self) -> float:
        data = float(self.get('r0x35')) * self._scale_factor
        logging.info(self._log_str(f" Following error: {data}"))

    def get_event_register(self) -> int:
        data = self.get('r0xa0')
        logging.info(self._log_str(f" Event register: {int(data):x}"))

    def enable_drive(self) -> None:
        logging.info(self._log_str(" Enable drive"))
        self.set("r0x24 21")

    def disable_drive(self) -> None:
        logging.info(self._log_str(" Disable drive"))
        self.set("r0x24 0")

logging.basicConfig(level=logging.INFO)

dev = CopMotor(PORT)
dev.get_motor_position()
dev.get_load_position()
dev.get_following_error()
dev.set_profile_acceleration(0)
dev.set_profile_deceleration(0)
dev.set_profile_velocity(0)
dev.set_mode_relative_move()
dev.set_mode_programmed_position()
dev.enable_drive()
dev.get_event_register()
dev.set_relative_move(100)
dev.trajectory()
for k in range(1):
    dev.get_motor_position()
    time.sleep(1)
dev.disable_drive()
