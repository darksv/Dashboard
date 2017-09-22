from base64 import b64decode
from functools import wraps
from flask_mail import Mail
from werkzeug.debug import get_current_traceback
from werkzeug.routing import Rule
import config
from flask import Flask, jsonify, request, g
from core import DB
from core.services.users import get_user_by_username

app = Flask('dashboard')
app.secret_key = config.SECRET_KEY
app.url_map.add(Rule('/api/<path:path>', endpoint='nonexistent_api_endpoint'))
mail = Mail(app)


@app.before_request
def before_api_request():
    with DB.connect() as db:
        auth = request.headers.get('Authorization', None)
        if not auth:
            g.api_user = None
            return

        auth_type, data = auth.split(' ')
        username, password = b64decode(data).decode('utf-8').split(':')
        g.api_user = get_user_by_username(db, username)
        if not g.api_user:
            return error('Authorization failed, invalid username and/or password', 401)


@app.after_request
def after_api_request(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5000'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization'

    return response


def error(message, status=404):
    return jsonify(error=dict(message=message, status=status)), status


def internal_error():
    return error('Internal error occurred, please try again later', 500)


def api_auth_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not g.api_user:
            return error('Authorization required', 401)
        return func(*args, **kwargs)
    return decorated_view


@app.endpoint('nonexistent_api_endpoint')
def api_nonexistent_endpoint(path):
    return error('Invalid endpoint or unsupported method', 400)


@app.errorhandler(500)
def error_500(e):
    traceback = get_current_traceback()
    mail.send_message(subject='Wystąpił błąd przy przetwarzaniu żądania',
                      body='Path: {url}\nMethod: {method}\n--------------------\n{trace}'.format(
                          url=request.url,
                          method=request.method,
                          trace=traceback.plaintext),
                      sender=('Panel statystyk', config.SENDER_EMAIL),
                      recipients=[config.ADMIN_EMAIL])
    return 'Error 500', 500


from api import channel, channels, device, notification, user
