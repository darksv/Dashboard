import config
import os
from flask import Flask, send_from_directory, jsonify, render_template, request, redirect, url_for, abort
from flask.ext import login as flask_login
from flask.ext.login import current_user
from app.channel_types import get_types, get_type_ids
from app.db import DB
from app.db.channels import get_channel, get_or_create_channel, update_channel, update_channel_value,\
    get_recent_channel_stats, get_channel_stats
from app.db.devices import get_all_devices, get_device, get_or_create_device
from app.db.users import get_user_by_id, get_user_by_username
from app.utils import localize_datetime


app = Flask('dashboard', static_folder='app/static', template_folder='app/templates')
app.secret_key = config.SECRET_KEY

app.jinja_env.filters['datetime'] = utils.format_datetime

js_vars = dict()


@app.before_request
def add_js_vars():
    js_vars['endpoint'] = request.endpoint
    js_vars['user'] = dict(
        name=current_user.name if not current_user.is_anonymous else None,
        hash=current_user.hash if not current_user.is_anonymous else None
    )


@app.context_processor
def inject_utils():
    return dict(path_with_mtime=lambda path: '{0}?{1}'.format(path, int(os.path.getmtime('./app/static' + path))))


@app.context_processor
def inject_js_vars():
    return dict(data=js_vars)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

if config.DEVELOPMENT:
    @app.route('/css/<path:path>')
    def send_css(path: str):
        return send_from_directory('app/static/css', path)

    @app.route('/js/<path:path>')
    def send_js(path: str):
        return send_from_directory('app/static/js', path)

    @app.route('/fonts/<path:path>')
    def send_font(path: str):
        return send_from_directory('app/static/fonts', path)


@app.route('/')
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


@app.route('/channel/<int:channel_id>')
def channel_details(channel_id: int):
    channel = get_channel(DB, channel_id)

    js_vars['channel_id'] = channel.id
    js_vars['channel_uuid'] = channel.uuid

    return render_template('channel_details.html', channel=channel)


@app.route('/channel/<int:channel_id>/settings', methods=['GET', 'POST'])
@flask_login.login_required
def channel_settings(channel_id: int):
    channel = get_channel(DB, channel_id)
    if channel is None:
        return redirect('/')

    if request.method == 'POST':
        channel_name = request.form.get('channel_name', '')
        try:
            channel_type = int(request.form.get('channel_type', 0))
        except ValueError:
            channel_type = 0
        channel_unit = request.form.get('channel_unit', '')

        if len(channel_name) <= 100 and channel_type in get_type_ids():
            update_channel(DB, channel_id, channel_name, channel_type, channel_unit)

            return redirect(url_for('channel_details', channel_id=channel_id))

        channel_data = request.form.args
    else:
        channel_data = channel

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

            return redirect(next_page or url_for('devices_list'))
        else:
            message = ('danger', 'Nieprawidłowe dane!')

    return render_template('login.html', message=message, next=next_page)


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))


@login_manager.user_loader
def user_loader(user_id):
    return get_user_by_id(DB, user_id)


@app.route('/getStats')
def channel_stats():
    period = request.args.get('type')
    channel_id = int(request.args.get('channelId'))

    channel = get_channel(DB, channel_id)
    if not channel:
        return jsonify()

    labels = []
    values = []

    if period == 'recent':
        for timestamp, value in get_recent_channel_stats(DB, channel_id, 30):
            labels.append(localize_datetime(timestamp).strftime('%H:%M'))
            values.append(value)
    elif period == 'custom':
        try:
            period_start = utils.parse_datetime(request.args.get('from'))
            period_end = utils.parse_datetime(request.args.get('to'))
        except ValueError:
            pass
        else:
            for dt, value in get_channel_stats(DB, channel_id, period_start, period_end):
                labels.append(dt)
                values.append(value)

    title = channel.name
    unit = channel.unit

    return jsonify(title=title, unit=unit, labels=labels, values=values)


@app.route('/updateChannel')
def channel_update():
    try:
        device_uuid = request.args.get('deviceUuid')
        channel_uuid = request.args.get('channelUuid')
        value = float(request.args.get('value'))

        device = get_or_create_device(DB, device_uuid)
        channel = get_or_create_channel(DB, channel_uuid, device_id=device.id)
        if update_channel_value(DB, channel.id, value):
            return '', 200
        else:
            return 'ERROR', 500
    except Exception:
        abort(403)
