import connexion as connexion
from flask_cors import CORS
from flask_jwt import JWT

from controllers.auth_controller import auth_controller
from controllers.controller_utils import page_not_found, server_error, check_encrypted_password, unauthorized
from controllers.device_controller import device_controller
from controllers.group_controller import group_controller
from data_access.user_repository import UserRepository

app = connexion.FlaskApp(
    __name__,
    specification_dir='swagger',
    options={
        "swagger_ui": True,
        "serve_spec": True
    }
)
app.add_api("openapi.yml", strict_validation=True)
flask_app = app.app
flask_app.register_blueprint(group_controller, url_prefix='/groups')
flask_app.register_blueprint(device_controller)
flask_app.register_blueprint(auth_controller, url_prefix='/auth')

flask_app.config["DEBUG"] = True
flask_app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
flask_app.config["TEMPLATES_AUTO_RELOAD"] = True
flask_app.config['JSON_SORT_KEYS'] = False
flask_app.config["SECRET_KEY"] = 'very-super-secret'
flask_app.config["JWT_REQUIRED_CLAIMS"] = ["userId"]
flask_app.config["JWT_VERIFY_EXPIRATION"] = False
flask_app.config["JWT_VERIFY_CLAIMS"] = ["userId"]

cors = CORS(flask_app)


def authenticate(username, password):
    user = UserRepository().get_user_by_username(username)

    if not check_encrypted_password(password, user["password"]):
        return unauthorized

    return user


def identity(payload):
    user_id = payload["userId"]
    return UserRepository().get_user_by_id(user_id)


jwt = JWT(flask_app, authenticate, identity, )


@flask_app.errorhandler(404)
def PageNotFound(exception):
    return page_not_found


@flask_app.errorhandler(500)
def ServerError(exception):
    return server_error


if __name__ == "__main__":
    app.run(host='127.0.0.1')

