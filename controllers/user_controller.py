from flask import Blueprint

user_controller = Blueprint('user_controller', __name__)


@user_controller.route("/")
def get_users():
    return "list of users"
