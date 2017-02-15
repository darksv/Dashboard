import config
import os
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, jsonify, render_template, request, redirect, url_for
from flask.ext import login as flask_login
from flask.ext.login import current_user
from app import utils
from app.channel_types import get_types
from app.db import DB
from app.db.channels import get_channel, get_or_create_channel, update_channel, update_channel_value,\
    get_recent_channel_stats, get_channel_stats, get_all_channels, update_channels_order, get_all_channels_ordered
from app.db.devices import get_all_devices, get_device, get_or_create_device
from app.db.watchers import get_watchers
from app.db.users import get_user_by_id, get_user_by_username
from app.schemas.channel import ChannelSchema
from app.schemas.watcher import WatcherSchema
from app.schemas.user import UserSchema


app = Flask('dashboard', static_folder='static', template_folder='app/templates')
app.secret_key = config.SECRET_KEY
app.jinja_env.filters['datetime'] = utils.format_datetime


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

if config.DEVELOPMENT:
    @app.route('/css/<path:path>')
    def send_css(path: str):
        return send_from_directory('static/css', path)

    @app.route('/js/<path:path>')
    def send_js(path: str):
        return send_from_directory('static/js', path)

    @app.route('/fonts/<path:path>')
    def send_font(path: str):
        return send_from_directory('static/fonts', path)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/devices')
def devices_list():
    devices = get_all_devices(DB)

    return render_template('devices.html', devices=devices)


@app.route('/device/<int:device_id>')
def device_details(device_id: int):
    device = get_device(DB, device_id)

    if device is None:
        return redirect(url_for('devices_list'))

    return render_template('device_details.html', device=device)


@app.route('/device/<int:device_id>/settings')
@flask_login.login_required
def device_settings(device_id: int):
    device = get_device(DB, device_id)

    if device is None:
        return redirect(url_for('devices_list'))

    return render_template('device_settings.html', device=device)


@app.route('/channel/<int:channel_id>/settings', methods=['GET', 'POST'])
@flask_login.login_required
def channel_settings(channel_id: int):
    channel = get_channel(DB, channel_id)
    if not channel:
        return redirect('/')

    schema = ChannelSchema()

    if request.method == 'POST':
        editable_fields = ('name', 'type', 'unit', 'color', 'disabled')

        data, errors = schema.load(request.form, partial=editable_fields)
        if not errors and update_channel(DB, channel_id, **data):
            return redirect(url_for('index', _anchor='/channel/{}'.format(channel_id)))
    else:
        data = {}

    channel_data, _ = schema.dump(channel)
    channel_data.update(**data)

    return render_template('channel_settings.html', channel=channel_data, channel_types=get_types())


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
            message = ('danger', 'Nieprawidłowe dane!')

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


@app.route('/api/getStats')
def channel_stats():
    period = request.args.get('type')
    channel_id = int(request.args.get('channelId'))

    channel = get_channel(DB, channel_id)
    if not channel:
        return jsonify()

    labels = []
    values = []

    if period == 'recent':
        period_end = datetime.now()
        period_start = period_end - timedelta(minutes=60)

        labels, values = zip(*get_recent_channel_stats(DB, channel_id, period_start, period_end))
    elif period == 'custom':
        try:
            period_start = utils.parse_datetime(request.args.get('from'))
            period_end = utils.parse_datetime(request.args.get('to'))
        except ValueError:
            pass
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


@app.route('/api/watchers')
def api_monitors():
    channel_id = request.args.get('channel_id')
    if channel_id:
        watchers = get_watchers(DB, channel_id)
        return jsonify(watchers=WatcherSchema().dump(watchers, many=True).data)


@app.route('/api/updateOrder', methods=['POST'])
def api_update_order():
    if current_user.is_authenticated:
        data = request.get_json()
        update_channels_order(DB, current_user.id, data['order'])
    return ''
