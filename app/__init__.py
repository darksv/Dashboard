import config
import os
from base64 import b64decode
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask.ext import login as flask_login
from flask.ext.login import current_user
from flask.ext.mail import Mail
from werkzeug.debug import get_current_traceback
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

app = Flask('dashboard', static_folder='static', template_folder='app/templates')
app.secret_key = config.SECRET_KEY
app.jinja_env.filters['datetime'] = utils.format_datetime
mail = Mail(app)


@app.context_processor
def inject_utils():
    return dict(path_with_mtime=lambda path: '{0}?{1}'.format(path, int(os.path.getmtime('./static' + path))))


@app.context_processor
def inject_variables():
    return dict(
        user=current_user
    )

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


def is_authorized(username, password):
    user = get_user_by_username(DB, username)
    return user and user.check_password(password)


def api_auth_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # noinspection PyBroadException
        try:
            auth_type, data = request.headers.get('Authorization', '').split(' ')
            if auth_type != 'Basic':
                return jsonify(), 401

            username, password = b64decode(data).decode('utf-8').split(':')
            if not is_authorized(username, password):
                return jsonify(), 401

            return func(*args, **kwargs)
        except:
            return jsonify(), 401

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


@app.route('/api/session')
def session():
    return jsonify(user=UserSchema().dump(current_user).data)


@app.route('/updateChannel')
def channel_update():
    device_uuid = request.args.get('deviceUuid')
    channel_uuid = request.args.get('channelUuid')

    device = get_or_create_device(DB, device_uuid)
    channel = get_or_create_channel(DB, channel_uuid, device_id=device.id)

    raw_value = request.args.get('value')

    if channel.type.name == 'float':
        value = float(raw_value)

        if update_channel_value(DB, channel.id, value):
            return str(channel.id), 200
        else:
            return 'ERROR', 500
    elif channel.type.name == 'color':
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
        return jsonify({}), 500

    return jsonify(id=notification_id)


@app.route('/api/notifications', methods=['GET'])
@api_auth_required
def api_notifications():
    notifications = get_pending_notifications(DB, current_user.id)
    return jsonify(NotificationSchema().dump(notifications, many=True).data)


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
            return jsonify(), 500
        else:
            if (period_end - period_start).total_seconds() > 0:
                labels, values = zip(*get_channel_stats(DB, channel_id, period_start, period_end))

    title = channel.name
    unit = channel.unit

    return jsonify(title=title, unit=unit, labels=labels, values=values)


@app.route('/api/channels')
def api_channels():
    if current_user.is_anonymous:
        channels = get_all_channels(DB)
    else:
        channels = get_all_channels_ordered(DB, current_user.id)

    return jsonify(channels=ChannelSchema().dump(channels, many=True).data)


@app.route('/api/channel/<int:channel_id>/watchers', methods=['GET'])
def api_channel_watchers(channel_id: int):
    watchers = get_watchers(DB, channel_id)

    return jsonify(watchers=WatcherSchema().dump(watchers, many=True).data)


@app.route('/api/device/<int:device_id>', methods=['GET'])
def device_settings(device_id: int):
    device = get_device(DB, device_id)
    if not device:
        return jsonify(), 404

    schema = DeviceSchema()
    data, _ = schema.dump(device)

    return jsonify(data), 200


@app.route('/api/channel/<int:channel_id>', methods=['GET'])
def api_channel_settings(channel_id: int):
    channel = get_channel(DB, channel_id)
    if not channel:
        return jsonify(), 404

    schema = ChannelSchema()
    data, _ = schema.dump(channel)
    return jsonify(data), 200


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
        return jsonify(), 200

    return jsonify(), 500


@app.route('/api/order', methods=['POST'])
@api_auth_required
def api_update_order():
    ids = list(map(int, request.args.get('order', '').split(',')))
    update_channels_order(DB, current_user.id, ids)
    return jsonify(), 200


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
