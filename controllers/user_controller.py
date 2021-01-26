import flask
from flask import Blueprint, request

from controllers.controller_utils import page_not_found, server_error
from data_access.user_repository import UserRepository

user_controller = Blueprint('user_controller', __name__)


@user_controller.route("/")
def get_users():
    return flask.jsonify(UserRepository().get_users())


@user_controller.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    return flask.jsonify(UserRepository().get_user(user_id))


@user_controller.route("/", methods=['POST'])
def add_user():
    if not request.json:
        return page_not_found

    model = request.json

    try:
        user_id = UserRepository().insert_user(model)

        return flask.jsonify(user_id)
    except:
        return server_error
