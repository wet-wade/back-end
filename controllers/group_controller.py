import flask

from flask import Blueprint, request
from controllers.controller_utils import page_not_found, server_error, MapCommand
from data_access.group_repository import GroupRepository

group_controller = Blueprint('group_controller', __name__)


@group_controller.route("/", methods=["GET"])
def get_groups():
    return flask.jsonify(GroupRepository().get_groups_summary_by_user("b956b391-c333-4017-967a-627fa6bd90a1"))


@group_controller.route("/<group_id>", methods=["GET"])
def get_group(group_id):
    return flask.jsonify(GroupRepository().get_group(group_id))


@group_controller.route("/<group_id>/summary", methods=["GET"])
def get_group_summary(group_id):
    return flask.jsonify(GroupRepository().get_group_summary_by_group(group_id))


@group_controller.route("/<group_id>/discover", methods=["GET"])
def discover(group_id):
    return flask.jsonify(GroupRepository().discover(group_id))


@group_controller.route("/", methods=["POST"])
def create_group():
    if not request.json:
        return page_not_found

    model = request.json

    try:
        result = GroupRepository().create_group(model)

        return flask.jsonify(result)
    except:
        return server_error


@group_controller.route("/<group_id>/devices", methods=["POST"])
def add_device(group_id):
    if not request.json:
        return page_not_found

    model = request.json

    return flask.jsonify(model)


@group_controller.route("/<group_id>/members", methods=["POST"])
def join_group(group_id):
    if not request.json:
        return page_not_found

    model = request.json

    return flask.jsonify(model)


@group_controller.route("/<group_id>/permissions", methods=["POST"])
def set_permissions(group_id):
    if not request.json:
        return page_not_found

    model = request.json

    return flask.jsonify(model)


@group_controller.route("/<group_id>/devices/<device_id>/command", methods=["POST"])
def control_device(group_id, device_id):
    body = request.get_json()
    command = body["command"]
    command_to_attribute = MapCommand(command)

    # if not ValidateAttribute(devices[device_id], command_to_attribute):
    #     return method_not_allowed
    #
    # if command == DeviceCommand.ON.name:
    #     devices[device_id].OnCommand()
    #     return flask.jsonify(status=devices[device_id].GetStatus())
    # elif command == DeviceCommand.OFF.name:
    #     devices[device_id].OffCommand()
    #     return flask.jsonify(status=devices[device_id].GetStatus())
    # elif command == DeviceCommand.LOCK.name:
    #     devices[device_id].Lock()
    #     return flask.jsonify(status=devices[device_id].GetStatus())
    # elif command == DeviceCommand.UNLOCK.name:
    #     devices[device_id].Unlock()
    #     return flask.jsonify(status=devices[device_id].GetStatus())
    # elif command == DeviceCommand.SET_TEMPERATURE.name:
    #     desired_temperature = int(body["input"])
    #     devices[device_id].SetDesiredTemperature(desired_temperature)
    #     return flask.jsonify(temperature=devices[device_id].GetTemperature())
    return page_not_found
