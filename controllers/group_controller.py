import flask
from flask import Blueprint, request

from controllers.controller_utils import page_not_found, server_error
from data_access.group_repository import GroupRepository

group_controller = Blueprint('group_controller', __name__)


@group_controller.route("/", methods=["GET"])
def get_groups():
    return flask.jsonify(GroupRepository().get_groups_by_user("b956b391-c333-4017-967a-627fa6bd90a1"))


@group_controller.route("/<group_id>", methods=["GET"])
def get_group(group_id):
    return flask.jsonify(GroupRepository().get_group(group_id))


@group_controller.route("/<group_id>/discover", methods=["GET"])
def discover(group_id):
    return f"Discovering devices in Group {group_id}"


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


@group_controller.route("/<group_id>/devices/<device_id>/<command>", methods=["POST"])
def control_device(group_id, device_id, command):
    if not request.json:
        return page_not_found

    model = request.json

    return flask.jsonify(model)
