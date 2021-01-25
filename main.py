import os
import random
import threading
import time
import flask

from enum import Enum
from flask import Response

from data_access.device_repository import DeviceRepository

method_not_allowed = Response("{'405':'Method not allowed'}", status=405, mimetype='application/json')


class Status(Enum):
    On = 1
    Off = 0


class GenericDevice:
    status = Status.On.value
    ip_address = ""
    mac_address = ""
    name = ""

    def __init__(self, ip_address, mac_address, name):
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.name = name

    def OnCommand(self):
        self.status = Status.On.value

    def OffCommand(self):
        self.status = Status.Off.value

    def GetStatus(self):
        return self.status

    def ToggleCommand(self):
        self.status = 1 - self.status


class LightBulb(GenericDevice):
    pass


class HVAC(GenericDevice):
    def SimulateTemperatureVariations(self):
        while True:
            variation = random.randint(-1, 1)
            self.temperature += variation * 0.5
            time.sleep(1)

    def __init__(self, ip_address, mac_address, name):
        super().__init__(ip_address, mac_address, name)
        x = threading.Thread(target=self.SimulateTemperatureVariations)
        x.start()

    def GetTemperature(self):
        return self.temperature

    temperature = 21.0


class Door(GenericDevice):
    pass


class Plug(GenericDevice):
    pass


door = Door("192.168.0.0", "6c:95:3f:11:0f:d8", "Smart Door")
plug = Plug("192.168.0.1", "99:84:b3:e3:7d:99", "Smart Plug")
hvac = HVAC("192.168.0.2", "c5:72:63:3b:fa:70", "Smart HVAC")
light_bulb = LightBulb("192.168.0.3", "33:6c:1e:b7:f5:24", "Smart Plug")

devices = {
    door.ip_address: door,
    plug.ip_address: plug,
    hvac.ip_address: hvac,
    light_bulb.ip_address: light_bulb
}

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


def ValidateAttribute(x, attribute):
    if hasattr(x, attribute):
        return True
    else:
        return


@app.route('/devices', methods=['GET'])
def get_devices():
    return flask.jsonify(DeviceRepository().get_devices())


@app.route('/<ip_address>/state', methods=['GET'])
def GetStatus(ip_address):
    if not ValidateAttribute(devices[ip_address], 'GetStatus'):
        return method_not_allowed
    return flask.jsonify(status=devices[ip_address].GetStatus())


@app.route('/<ip_address>/toggle', methods=['GET'])
def ToggleStatus(ip_address):
    if not ValidateAttribute(devices[ip_address], 'ToggleCommand'):
        return method_not_allowed
    devices[ip_address].ToggleCommand()
    return flask.jsonify(status=devices[ip_address].GetStatus())


@app.route('/<ip_address>/temperature', methods=['GET'])
def GetTemperature(ip_address):
    if not ValidateAttribute(devices[ip_address], 'GetTemperature'):
        return method_not_allowed
    return flask.jsonify(temperature=devices[ip_address].GetTemperature())


@app.route('/<ip_address>/open', methods=['GET'])
@app.route('/<ip_address>/on', methods=['GET'])
def ToggleOnStatus(ip_address):
    if not ValidateAttribute(devices[ip_address], 'GetStatus') or not ValidateAttribute(devices[ip_address], 'OnCommand'):
        return method_not_allowed
    devices[ip_address].OnCommand()
    return flask.jsonify(status=devices[ip_address].GetStatus())


@app.route('/<ip_address>/close', methods=['GET'])
@app.route('/<ip_address>/off', methods=['GET'])
def ToggleOffStatus(ip_address):
    if not ValidateAttribute(devices[ip_address], 'GetStatus') or not ValidateAttribute(devices[ip_address], 'OffCommand'):
        return method_not_allowed
    devices[ip_address].OffCommand()
    return flask.jsonify(status=devices[ip_address].GetStatus())


@app.route('/discover', methods=['GET'])
def Discover():
    connected_devices = {}
    for device in devices:
        connected_devices[device] = devices[device].name
    return flask.jsonify(connected_devices)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

