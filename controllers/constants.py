from enum import Enum


class DeviceStatus(Enum):
    ON = 1
    OFF = 0


class DeviceType(Enum):
    LIGHTBULB = 'lightbulb',
    HVAC = 'hvac',
    DOOR = 'door',
    OUTLET = 'outlet'


class DeviceCommand(Enum):
    ON = 'ON',
    OFF = 'OFF',
    SET_TEMPERATURE = 'SET_TEMPERATURE',
    LOCK = 'LOCK',
    UNLOCK = 'UNLOCK'
