from flask import Response

method_not_allowed = Response("{'405':'Method not allowed'}", status=405, mimetype='application/json')
page_not_found = Response("{'404':'Not found'}", status=404, mimetype='application/json')
server_error = Response("{'500':'Internal server error'}", status=500, mimetype='application/json')


def ValidateAttribute(x, attribute):
    if hasattr(x, attribute):
        return True
    else:
        return