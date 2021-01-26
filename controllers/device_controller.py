import json
import random
import threading
import time
import flask

from flask import Blueprint, request
from controllers.constants import DeviceStatus, DeviceCommand, DeviceType
from controllers.controller_utils import method_not_allowed, ValidateAttribute, MapCommand, get_uuid, NewDeviceMapping, SavedDeviceMapping
from data_access.device_repository import DeviceRepository

device_controller = Blueprint('device_controller', __name__)


class GenericDevice:
    def __init__(self, name):
        self.id = get_uuid()
        self.name = name
        self.nickname = ""
        self.available = False
        self.status = DeviceStatus.OFF.value
        self.data = {}

    def OnCommand(self):
        self.status = DeviceStatus.ON.value

    def OffCommand(self):
        self.status = DeviceStatus.OFF.value

    def GetStatus(self):
        return self.status

    def ToggleCommand(self):
        self.status = 1 - self.status


class LightBulb(GenericDevice):
    def __init__(self, name):
        super().__init__(name)
        self.type = DeviceType.LIGHTBULB


class HVAC(GenericDevice):
    def SimulateTemperatureVariations(self):
        while True:
            variation = random.randint(-1, 1)
            self.data["temperature"] += variation * 0.5
            time.sleep(5)

    def RegulateTemperature(self):
        while True:
            if self.status == DeviceStatus.ON.value:
                if round(self.data["temperature"], 1) > self.data["desired_temperature"]:
                    self.data["temperature"] -= 0.1
                elif round(self.data["temperature"], 1) < self.data["desired_temperature"]:
                    self.data["temperature"] += 0.1
            time.sleep(0.5)

    def __init__(self, name):
        super().__init__(name)
        self.type = DeviceType.HVAC
        self.data = {
            "temperature": 21.0,
            "desired_temperature": 21.0
        }
        x = threading.Thread(target=self.SimulateTemperatureVariations)
        x.start()
        y = threading.Thread(target=self.RegulateTemperature)
        y.start()

    def SetDesiredTemperature(self, temperature):
        self.data["desired_temperature"] = temperature
        return self.data["desired_temperature"]

    def GetTemperature(self):
        return round(self.data["temperature"], 1)


class Door(GenericDevice):
    def __init__(self, name):
        super().__init__(name)
        self.type = DeviceType.DOOR
        self.data = {
            "locked": False
        }

    def Lock(self):
        self.data["locked"] = True
        return self.data["locked"]

    def Unlock(self):
        self.data["locked"] = False
        return self.data["locked"]

    def GetLockStatus(self):
        return self.data["locked"]


class Outlet(GenericDevice):
    def __init__(self, name):
        super().__init__(name)
        self.type = DeviceType.OUTLET


door = Door("Smart Door")
outlet = Outlet("Smart Outlet")
hvac = HVAC("Smart HVAC")
light_bulb = LightBulb("Smart LightBulb")

devices = {
    door.id.__str__(): door,
    outlet.id.__str__(): outlet,
    hvac.id.__str__(): hvac,
    light_bulb.id.__str__(): light_bulb
}


@device_controller.route('/groups/<group_id>/devices/<device_id>/command', methods=['POST'])
def ControlDevice(group_id, device_id):
    body = request.get_json()
    command = body["command"]
    command_to_attribute = MapCommand(command)
    print(command)
    print(command_to_attribute)
    if not ValidateAttribute(devices[device_id], command_to_attribute):
        return method_not_allowed

    if command == DeviceCommand.ON.name:
        devices[device_id].OnCommand()
        return flask.jsonify(status=devices[device_id].GetStatus())
    elif command == DeviceCommand.OFF.name:
        devices[device_id].OffCommand()
        return flask.jsonify(status=devices[device_id].GetStatus())
    elif command == DeviceCommand.LOCK.name:
        devices[device_id].Lock()
        return flask.jsonify(status=devices[device_id].GetStatus())
    elif command == DeviceCommand.UNLOCK.name:
        devices[device_id].Unlock()
        return flask.jsonify(status=devices[device_id].GetStatus())
    elif command == DeviceCommand.SET_TEMPERATURE.name:
        desired_temperature = int(body["input"])
        devices[device_id].SetDesiredTemperature(desired_temperature)
        return flask.jsonify(temperature=devices[device_id].GetTemperature())


@device_controller.route('/devices/discover', methods=['POST'])
def Discover():
    response = []
    for device_id in devices:
        response.append(NewDeviceMapping(devices[device_id]))
    return flask.jsonify(response)


@device_controller.route('/groups/<group_id>/devices', methods=['GET'])
def GetDevices(group_id):
    response = []
    for device_id in devices:
        response.append(SavedDeviceMapping(devices[device_id]))
    return flask.jsonify(response)


@device_controller.route('/groups/<group_id>/devices', methods=['POST'])
def AddDevice(group_id):
    body = request.get_json()
    device_id = body["deviceId"]
    nickname = body["nickname"]
    return flask.jsonify({
        "id": device_id,
        "nickname": nickname
    })
