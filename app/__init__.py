import config
import os
from flask import Flask, send_from_directory, jsonify, render_template, request, redirect, url_for
from flask_restful import Api
from flask.ext import login as flask_login
from app import utils
from app.resources.channel import ChannelResource
from app.resources.channel_stats import ChannelStatsResource
from app.resources.device import DeviceResource


app = Flask('dashboard', static_folder='app/static', template_folder='app/templates')
app.secret_key = config.SECRET_KEY

app.jinja_env.filters['datetime'] = utils.format_datetime
app.jinja_env.filters['script_mod_time'] = lambda name:\
    int(os.path.getmtime(os.path.join('.', 'app', 'static', 'js', name)))

api = Api(app)
api.add_resource(ChannelResource, '/channels')
api.add_resource(ChannelResource, '/channels/<int:channel_id>', endpoint='channels')
api.add_resource(ChannelStatsResource, '/channels/<int:channel_id>/stats/<string:period>')
api.add_resource(DeviceResource, '/devices')
api.add_resource(DeviceResource, '/devices/<int:device_id>', endpoint='devices')

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
    devices = DeviceResource().get()['data']

    return render_template('devices.html', devices=devices)


@app.route('/device/<int:device_id>')
@flask_login.login_required
def device_details(device_id: int):
    device_data = DeviceResource().get(device_id)['data']

    return render_template('device_details.html', device=device_data)


@app.route('/channel/<int:channel_id>')
@flask_login.login_required
def channel_details(channel_id: int):
    channel_data = ChannelResource().get(channel_id)['data']

    return render_template('channel_details.html', channel=channel_data)


@app.route('/login', methods=['GET', 'POST'])
@login_manager.unauthorized_handler
def login():
    message = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in config.USERS and config.USERS[username] == password:
            user = User()
            user.id = username

            flask_login.login_user(user)
        else:
            message = ('danger', 'Nieprawidłowe dane!')

    return render_template('login.html', message=message)


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(username):
    if username not in config.USERS:
        return

    user = User()
    user.id = username

    return user
