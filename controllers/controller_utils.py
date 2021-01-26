import uuid

from enum import Enum
from flask import Response
from passlib.context import CryptContext
from controllers.constants import DeviceCommand

method_not_allowed = Response("{'405':'Method not allowed'}", status=405, mimetype='application/json')
page_not_found = Response("{'404':'Not found'}", status=404, mimetype='application/json')
server_error = Response("{'500':'Internal server error'}", status=500, mimetype='application/json')
not_acceptable = Response("{'406':'Not acceptable'}", status=406, mimetype='application/json')
created = Response("{'201':'Created'}", status=201, mimetype='application/json')

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)


def get_uuid():
    return str(uuid.uuid4())


def encrypt_password(password):
    return pwd_context.encrypt(password)


def check_encrypted_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def ValidateAttribute(x, attribute):
    if hasattr(x, attribute):
        return True
    else:
        return


def MapCommand(command):
    if command == DeviceCommand.ON.name:
        return "OnCommand"
    elif command == DeviceCommand.OFF.name:
        return "OffCommand"
    elif command == DeviceCommand.LOCK.name:
        return "Lock"
    elif command == DeviceCommand.UNLOCK.name:
        return "Unlock"
    elif command == DeviceCommand.SET_TEMPERATURE.name:
        return "SetDesiredTemperature"
    else:
        return "Invalid"


def NewDeviceMapping(device):
    return {
        "id": device.id,
        "name": device.name,
        "type": device.type.name,
    }


def SavedDeviceMapping(device):
    return {
        "nickname": device.nickname,
        "available": device.available,
        "status": device.status,
        "data": device.data
    }