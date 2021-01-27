import flask
import jwt
import redis

from flask import Blueprint, request
from flask_jwt import jwt_required, current_identity
from controllers.controller_utils import page_not_found, server_error, MapCommand, bad_request, get_uuid, unauthorized, \
    ok
from data_access.group_repository import GroupRepository
from data_access.permission_repository import PermissionRepository

group_controller = Blueprint('group_controller', __name__)


@group_controller.route("/", methods=["GET"])
@jwt_required()
def get_groups():
    return flask.jsonify({
        "groups": GroupRepository().get_groups_summary_by_user(current_identity["id"])
    })


@group_controller.route("/<group_id>", methods=["GET"])
@jwt_required()
def get_group(group_id):
    return flask.jsonify({
        "device": GroupRepository().get_group(group_id)
    })


@group_controller.route("/<group_id>/summary", methods=["GET"])
@jwt_required()
def get_group_summary(group_id):
    return flask.jsonify(GroupRepository().get_group_summary_by_group(group_id))


@group_controller.route("/<group_id>/discover", methods=["GET"])
@jwt_required()
def discover(group_id):
    return flask.jsonify(GroupRepository().discover(group_id))


@group_controller.route("/", methods=["POST"])
@jwt_required()
def create_group():
    if not request.json:
        return page_not_found

    model = request.json

    try:
        group_id = GroupRepository().create_group(model["name"])

        return flask.jsonify({
            "group": GroupRepository().get_group_summary_by_group(group_id)
        })
    except:
        return server_error


@group_controller.route("/<group_id>/devices", methods=["POST"])
@jwt_required()
def add_device(group_id):
    if not request.json:
        return page_not_found

    body = request.json
    device_id = body["deviceId"]

    GroupRepository().insert_new_device(group_id, device_id)

    return flask.jsonify(body)


@group_controller.route("/<group_id>/members", methods=["POST"])
# @jwt_required()
def join_group(group_id):
    if not request.json:
        return page_not_found

    if 'Authorization' not in request.headers:
        user_name = request.json["name"]
        user_id = get_uuid()
        token = jwt.encode({
            'userId': user_id,
            'name': user_name
        }, 'very-super-secret')
        response = {
            "visitor": {
                "userId": user_id,
                "name": user_name
            },
            "token": token.decode("utf-8")
        }

        GroupRepository().create_visitor(user_id, group_id, user_name)

        return flask.jsonify(response)
    else:
        token = jwt.decode()
        user_id = token["userId"]
        user_name = token["name"]
        if not GroupRepository().find_user(user_id):
            return unauthorized
        else:
            GroupRepository().insert_user_group(group_id, user_name)
            return ok


@group_controller.route("/<group_id>/permissions", methods=["POST"])
@jwt_required()
def set_permissions(group_id):
    if not request.json:
        return page_not_found
    if not request.json.get("permissions", None):
        return bad_request

    model = request.json["permissions"]
    user_id = current_identity["id"]

    result = PermissionRepository().set_permission(group_id, user_id, model)

    return flask.jsonify(result)


@group_controller.route("/<group_id>/devices/<device_id>/command", methods=["POST"])
@jwt_required()
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
