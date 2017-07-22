from base64 import b64decode
from functools import wraps
from flask_login import LoginManager
from flask_mail import Mail
from werkzeug.debug import get_current_traceback
from werkzeug.routing import Rule
import config
from flask import Flask, jsonify, render_template, request, redirect, url_for
from core import utils, DB
from core.services.users import get_user_by_username, get_user_by_id

app = Flask('dashboard', static_folder='frontend/dist', template_folder='app/templates')
app.secret_key = config.SECRET_KEY
app.jinja_env.filters['datetime'] = utils.format_datetime
app.url_map.add(Rule('/api/<path:path>', endpoint='nonexistent_api_endpoint'))
login_manager = LoginManager(app)
mail = Mail(app)
api_user = None


@app.before_request
def before_api_request():
    with DB.connect() as db:
        global api_user

        auth = request.headers.get('Authorization', None)
        if not auth:
            api_user = None
            return

        auth_type, data = auth.split(' ')
        username, password = b64decode(data).decode('utf-8').split(':')
        api_user = get_user_by_username(db, username)
        if not api_user:
            return error('Authorization failed, invalid username and/or password', 401)


def error(message, status=404):
    return jsonify(error=dict(message=message, status=status)), status


def internal_error():
    return error('Internal error occurred, please try again later', 500)


def api_auth_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not api_user:
            return error('Authorization required', 401)

        return func(*args, **kwargs)

    return decorated_view


@app.route('/')
def index():
    return render_template('index.html')


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login', next=request.path))


@login_manager.user_loader
def user_loader(user_id):
    with DB.connect() as c:
        return get_user_by_id(c, user_id)


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
