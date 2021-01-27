import flask
import jwt
from flask import Blueprint, request
from flask_jwt import jwt_required, current_identity

from controllers.controller_utils import page_not_found, check_encrypted_password, unauthorized, server_error, \
    bad_request, get_token_info
from data_access.user_repository import UserRepository

auth_controller = Blueprint('auth_controller', __name__)


@auth_controller.route("/login", methods=['POST'])
def login():
    if not request.json:
        return page_not_found

    model = request.json

    user = UserRepository().get_user_by_username(model["username"], True)

    if not check_encrypted_password(model["password"], user["password"]):
        return unauthorized

    token = jwt.encode({
        'userId': user['id'],
        'name': user['name']
    }, 'very-super-secret')

    return {
        "user": user,
        "authToken": f"{token.decode('utf-8')}"
    }


@auth_controller.route('/register', methods=['POST'])
def register():
    if not request.json:
        return page_not_found

    model = request.json

    try:
        user = UserRepository().insert_user(model)

        token = jwt.encode({
            'userId': user['id'],
            'name': user['name']
        }, 'very-super-secret')

        return {
            "user": user,
            "authToken": f"{token.decode('utf-8')}"
        }
    except:
        return server_error


@auth_controller.route('/token', methods=['POST'])
def auth_token():
    if not request.json:
        return bad_request

    token = get_token_info(request.json["token"])

    user = UserRepository().get_user_by_id(token["userId"])

    return {
        "user": user
    }
