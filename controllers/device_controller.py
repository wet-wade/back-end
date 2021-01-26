import flask

from flask import Blueprint
from controllers.controller_utils import NewDeviceMapping
from mock.mock_devices import devices


device_controller = Blueprint('device_controller', __name__)


@device_controller.route('/devices/discover', methods=['POST'])
def Discover():
    response = []
    for device_id in devices:
        response.append(NewDeviceMapping(devices[device_id]))
    return flask.jsonify(response)
