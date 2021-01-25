from flask import Blueprint

group_controller = Blueprint('group_controller', __name__)


@group_controller.route("/")
def get_groups():
    return "list of groups"
