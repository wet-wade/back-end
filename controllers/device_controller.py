import random
import threading
import time
import uuid
from enum import Enum


import flask
from flask import Blueprint, request

from controllers.controller_utils import method_not_allowed, ValidateAttribute
from data_access.device_repository import DeviceRepository

device_controller = Blueprint('device_controller', __name__)


class DeviceStatus(Enum):
    ON = 1
    OFF = 0


class GenericDevice:
    status = DeviceStatus.OFF.value
    name = ""
    id = ""
    data = {}

    def __init__(self, name):
        self.name = name
        self.id = uuid.uuid4()

    def OnCommand(self):
        self.status = DeviceStatus.ON.value

    def OffCommand(self):
        self.status = DeviceStatus.OFF.value

    def GetStatus(self):
        return self.status

    def ToggleCommand(self):
        self.status = 1 - self.status


class LightBulb(GenericDevice):
    pass


class HVAC(GenericDevice):
    data = {
        "temperature": 21.0,
        "desired_temperature": 21.0
    }

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
    data = {
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
    pass


door = Door("Smart Door")
plug = Outlet("Smart Outlet")
hvac = HVAC("Smart HVAC")
light_bulb = LightBulb("Smart LightBulb")

devices = {
    door.id.__str__(): door,
    plug.id.__str__(): plug,
    hvac.id.__str__(): hvac,
    light_bulb.id.__str__(): light_bulb
}


@device_controller.route('/', methods=['GET'])
def get_devices():
    return flask.jsonify(DeviceRepository().get_devices())


@device_controller.route('/<device_id>/status', methods=['GET'])
def GetStatus(device_id):
    if not ValidateAttribute(devices[device_id], 'GetStatus'):
        return method_not_allowed
    return flask.jsonify(status=devices[device_id].GetStatus())


@device_controller.route('/<device_id>/toggle', methods=['GET'])
def ToggleStatus(device_id):
    if not ValidateAttribute(devices[device_id], 'ToggleCommand'):
        return method_not_allowed
    devices[device_id].ToggleCommand()
    return flask.jsonify(status=devices[device_id].GetStatus())


@device_controller.route('/<device_id>/temperature', methods=['GET'])
def GetTemperature(device_id):
    if not ValidateAttribute(devices[device_id], 'GetTemperature'):
        return method_not_allowed
    return flask.jsonify(temperature=devices[device_id].GetTemperature())


@device_controller.route('/<device_id>/temperature', methods=['POST'])
def SetTemperature(device_id):
    if not ValidateAttribute(devices[device_id], 'SetDesiredTemperature'):
        return method_not_allowed
    body = request.get_json()
    desired_temperature = int(body["desired_temperature"])
    return flask.jsonify(temperature=devices[device_id].SetDesiredTemperature(desired_temperature))


@device_controller.route('/<device_id>/on', methods=['GET'])
def ToggleOnStatus(device_id):
    if not ValidateAttribute(devices[device_id], 'GetStatus'):
        return method_not_allowed
    devices[device_id].OnCommand()
    return flask.jsonify(status=devices[device_id].GetStatus())


@device_controller.route('/<device_id>/off', methods=['GET'])
def ToggleOffStatus(device_id):
    if not ValidateAttribute(devices[device_id], 'GetStatus'):
        return method_not_allowed
    devices[device_id].OffCommand()
    return flask.jsonify(status=devices[device_id].GetStatus())


@device_controller.route('/<device_id>/lock', methods=['GET'])
def Lock(device_id):
    if not ValidateAttribute(devices[device_id], 'Lock'):
        return method_not_allowed
    devices[device_id].Lock()
    return flask.jsonify(locked=devices[device_id].GetLockStatus())


@device_controller.route('/<device_id>/unlock', methods=['GET'])
def Unlock(device_id):
    if not ValidateAttribute(devices[device_id], 'Unlock'):
        return method_not_allowed
    devices[device_id].Unlock()
    return flask.jsonify(locked=devices[device_id].GetLockStatus())


@device_controller.route('/discover', methods=['GET'])
def Discover():
    connected_devices = {}
    for device in devices:
        connected_devices[device] = devices[device].name
    return flask.jsonify(connected_devices)