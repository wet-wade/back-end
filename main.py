import connexion as connexion

from controllers.controller_utils import page_not_found, server_error
from controllers.device_controller import device_controller
from controllers.group_controller import group_controller
from controllers.user_controller import user_controller
from flask_cors import CORS


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
flask_app.register_blueprint(user_controller, url_prefix='/users')
flask_app.register_blueprint(group_controller, url_prefix='/groups')
flask_app.register_blueprint(device_controller)

flask_app.config["DEBUG"] = True
flask_app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
flask_app.config["TEMPLATES_AUTO_RELOAD"] = True
flask_app.config['JSON_SORT_KEYS'] = False

cors = CORS(flask_app)


@flask_app.errorhandler(404)
def PageNotFound(exception):
    return page_not_found


@flask_app.errorhandler(500)
def ServerError(exception):
    return server_error


if __name__ == "__main__":
    app.run(host='127.0.0.1')

