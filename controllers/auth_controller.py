import flask
from flask import Blueprint, request, app
from flask_jwt import JWT

from controllers.controller_utils import page_not_found, server_error, check_encrypted_password, unauthorized
from data_access.user_repository import UserRepository

auth_controller = Blueprint('auth_controller', __name__)


@auth_controller.route("/login", methods=['POST'])
def login():
    if not request.json:
        return page_not_found

    model = request.json

    # if authenticate(model["password"], )

    user = UserRepository().get_user_by_username(model["username"])

    if not check_encrypted_password(model["password"], user["password"]):
        return unauthorized

    return user


@auth_controller.route('/register', methods=['POST'])
def register(user_id):
    return flask.jsonify(UserRepository().get_user_by_id(user_id))


@auth_controller.route('/token', methods=['POST'])
def auth_token(user_id):
    return flask.jsonify(UserRepository().get_user_by_id(user_id))
