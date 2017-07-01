import config
import os
from base64 import b64decode
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask.ext.login import LoginManager
from flask.ext import login as flask_login
from flask.ext.mail import Mail
from werkzeug.debug import get_current_traceback
from werkzeug.routing import Rule
from app import utils
from app.db import DB
from app.db.channels import get_channel, get_or_create_channel, update_channel, update_channel_value,\
    get_recent_channel_stats, get_channel_stats, get_all_channels, update_channels_order, get_all_channels_ordered
from app.db.devices import get_device, get_or_create_device
from app.db.notification import create_notification, get_pending_notifications
from app.db.watchers import get_watchers
from app.db.users import get_user_by_id, get_user_by_username
from app.schemas.channel import ChannelSchema
from app.schemas.device import DeviceSchema
from app.schemas.watcher import WatcherSchema
from app.schemas.notification import NotificationSchema
from app.schemas.user import UserSchema
from app.channel_type import ChannelType

app = Flask('dashboard', static_folder='static', template_folder='app/templates')
app.secret_key = config.SECRET_KEY
app.jinja_env.filters['datetime'] = utils.format_datetime
app.url_map.add(Rule('/api/<path:path>', endpoint='nonexistent_api_endpoint'))
login_manager = LoginManager(app)
mail = Mail(app)
api_user = None


@app.context_processor
def inject_utils():
    return dict(path_with_mtime=lambda path: '{0}?{1}'.format(path, int(os.path.getmtime('./static' + path))))


@app.before_request
def before_api_request():
    global api_user

    auth = request.headers.get('Authorization', None)
    if not auth:
        api_user = None
        return

    auth_type, data = auth.split(' ')
    username, password = b64decode(data).decode('utf-8').split(':')
    api_user = get_user_by_username(DB, username)
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    next_page = request.args.get('next', None)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = get_user_by_username(DB, username)

        if user and user.check_password(password):
            flask_login.login_user(user)

            return redirect(next_page or url_for('index'))
        else:
            message = ('error', 'Nieprawidłowe dane!')

    return render_template('login.html', message=message, next=next_page)


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(request.referrer or url_for('index'))


@login_manager.user_loader
def user_loader(user_id):
    return get_user_by_id(DB, user_id)


@app.endpoint('nonexistent_api_endpoint')
def api_nonexistent_endpoint(path):
    return error('Invalid endpoint or unsupported method', 400)


@app.route('/channelUpdate', methods=['POST'])
def channel_update():
    device_uuid = request.form.get('device_uuid')
    channel_uuid = request.form.get('channel_uuid')
    raw_value = request.form.get('value')

    device = get_or_create_device(DB, device_uuid)
    channel = get_or_create_channel(DB, channel_uuid, device_id=device.id)

    if channel.type is ChannelType.FLOATING:
        value = float(raw_value)

        update_channel_value(DB, channel.id, value)
        return str(channel.id), 200

    elif channel.type is ChannelType.COLOR:
        value = utils.parse_color(raw_value)
        return ' ' .join(map(str, value))


@app.route('/api/notification', methods=['POST'])
def new_notification():
    data, errors = NotificationSchema().load(request.get_json() or request.args)
    if errors:
        return jsonify(errors=errors)

    user_id = data['user_id']
    watcher_id = data['watcher_id']
    message = data['message']

    notification_id = create_notification(DB, user_id, message, watcher_id)
    if not notification_id:
        return internal_error()

    return jsonify()


@app.route('/api/notifications', methods=['GET'])
@api_auth_required
def api_notifications():
    notifications = get_pending_notifications(DB, api_user.id)
    return jsonify(notifications=NotificationSchema().dump(notifications, many=True).data)


@app.route('/api/channel/<int:channel_id>/stats')
def api_channel_stats(channel_id: int):
    channel = get_channel(DB, channel_id)
    if not channel:
        return jsonify()

    labels = []
    values = []

    period = request.args.get('type', 'recent')
    if period == 'recent':
        period_end = datetime.now()
        period_start = period_end - timedelta(minutes=60)

        labels, values = zip(*get_recent_channel_stats(DB, channel_id, period_start, period_end))
    elif period == 'custom':
        try:
            period_start = utils.parse_datetime(request.args.get('from'))
            period_end = utils.parse_datetime(request.args.get('to'))
        except ValueError:
            return error('Bad request', 400)
        else:
            if (period_end - period_start).total_seconds() > 0:
                labels, values = zip(*get_channel_stats(DB, channel_id, period_start, period_end))

    title = channel.name
    unit = channel.unit

    return jsonify(title=title, unit=unit, labels=labels, values=values)


@app.route('/api/channels', methods=['GET'])
def api_channels():
    channels = get_all_channels_ordered(DB, api_user.id) if api_user else get_all_channels(DB)
    data, errors = ChannelSchema().dump(channels, many=True)
    return jsonify(channels=data) if not errors else internal_error()


@app.route('/api/channel/<int:channel_id>/watchers', methods=['GET'])
def api_channel_watchers(channel_id: int):
    watchers = get_watchers(DB, channel_id)
    data, errors = WatcherSchema().dump(watchers, many=True)
    return jsonify(watchers=data) if not errors else internal_error()


@app.route('/api/device/<int:device_id>', methods=['GET'])
def device_settings(device_id: int):
    device = get_device(DB, device_id)
    if not device:
        return error('Device not found')

    data, errors = DeviceSchema().dump(device)
    return jsonify(data) if not errors else internal_error()


@app.route('/api/channel/<int:channel_id>', methods=['GET'])
def api_channel_settings(channel_id: int):
    channel = get_channel(DB, channel_id)
    if not channel:
        return error('Channel not found')

    data, errors = ChannelSchema().dump(channel)
    return jsonify(data) if not errors else internal_error()


@app.route('/api/channel/<int:channel_id>', methods=['POST'])
@api_auth_required
def api_channel_update(channel_id: int):
    channel = get_channel(DB, channel_id)
    if not channel:
        return jsonify(), 404

    data, errors = ChannelSchema().load(request.get_json() or request.args)
    if errors:
        return jsonify(errors=errors), 400

    if update_channel(DB, channel_id, **data):
        return jsonify()

    return jsonify(), 500


@app.route('/api/order', methods=['POST'])
@api_auth_required
def api_update_order():
    ids = list(map(int, request.args.get('order', '').split(',')))
    update_channels_order(DB, api_user.id, ids)
    return jsonify()


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
