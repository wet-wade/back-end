import flask

from flask import Blueprint, request
from controllers.controller_utils import NewDeviceMapping, page_not_found, server_error

# from mock.mock_devices import devices

from data_access.device_repository import DeviceRepository

device_controller = Blueprint('device_controller', __name__)


@device_controller.route('/devices/test/', methods=["GET"])
def test():
    return flask.jsonify(DeviceRepository().get_device_definition_by_type("door"))


@device_controller.route('/devices/test/', methods=["POST"])
def test_insert():
    if not request.json:
        return page_not_found

    model = request.json

    try:
        result = DeviceRepository().insert_device(model)

        return flask.jsonify(result)
    except:
        return server_error


@device_controller.route('/devices/discover', methods=['POST'])
def Discover():
    response = []
    # for device_id in devices:
    #     response.append(NewDeviceMapping(devices[device_id]))
    # return flask.jsonify(response)
