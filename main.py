import flask

from controllers.controller_utils import page_not_found, server_error
from controllers.device_controller import device_controller
from controllers.group_controller import group_controller
from controllers.user_controller import user_controller


app = flask.Flask(__name__)
app.register_blueprint(user_controller, url_prefix='/users')
app.register_blueprint(group_controller, url_prefix='/groups')
app.register_blueprint(device_controller, url_prefix='/devices')

app.config["DEBUG"] = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.errorhandler(404)
def PageNotFound(exception):
    return page_not_found


@app.errorhandler(500)
def PageNotFound(exception):
    return server_error


if __name__ == "__main__":
    app.run()

