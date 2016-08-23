import config
import os
from flask import Flask, send_from_directory, jsonify, render_template, request, redirect, url_for, abort
from flask.ext import login as flask_login
from app.db import DB
from app.db.channels import update_channel, get_channel, get_recent_channel_stats, get_daily_channel_stats, get_monthly_channel_stats
from app.db.devices import get_all_devices, get_device
from app.db.users import get_user_by_username
from app.utils import localize_datetime


app = Flask('dashboard', static_folder='app/static', template_folder='app/templates')
app.secret_key = config.SECRET_KEY

app.jinja_env.filters['datetime'] = utils.format_datetime
app.jinja_env.filters['script_mod_time'] = lambda name:\
    int(os.path.getmtime(os.path.join('.', 'app', 'static', 'js', name)))

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

    return render_template('channel_details.html', channel=channel, data=dict(channel_uuid=channel.uuid))


@app.route('/channel/<int:channel_id>/settings', methods=['GET', 'POST'])
@flask_login.login_required
def channel_settings(channel_id: int):
    channel_data = get_channel(DB, channel_id)

    if request.method == 'POST':
        channel_name = request.form.get('channel_name', '')
        try:
            channel_type = int(request.form.get('channel_type', 0))
        except ValueError:
            channel_type = 0

        if len(channel_name) <= 100 and channel_type in (0, 1):
            update_channel(DB, channel_id, channel_name, channel_type)

            return redirect(url_for('channel_details', channel_id=channel_id))

        channel_data.update(name=channel_name, type=channel_type)

    return render_template('channel_settings.html', channel=channel_data)


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
    return get_user_by_username(DB, user_id)


@app.route('/channel/<int:channel_id>/stats/<period>')
def channel_stats(channel_id: int, period: str):
    data = []

    if period == 'recent':
        data = []
        for timestamp, value in get_recent_channel_stats(DB, channel_id, 100):
            data.append((localize_datetime(timestamp).isoformat(), value))
    elif period == 'daily':
        data = get_daily_channel_stats(DB, channel_id)
    elif period == 'monthly':
        data = get_monthly_channel_stats(DB, channel_id)

    return jsonify(items=data)
