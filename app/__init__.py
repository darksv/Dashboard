import config
import os
from flask import Flask, send_from_directory, jsonify, render_template
from flask_restful import Api
from app import utils
from app.resources.channel import ChannelResource
from app.resources.channel_stats import ChannelStatsResource
from app.resources.device import DeviceResource
from app.resources.entry import EntryResource


app = Flask('dashboard', static_folder='app/static', template_folder='app/templates')

app.jinja_env.filters['datetime'] = utils.format_datetime
app.jinja_env.filters['script_mod_time'] = lambda name:\
    int(os.path.getmtime(os.path.join('.', 'app', 'static', 'js', name)))

api = Api(app)
api.add_resource(ChannelResource, '/channels')
api.add_resource(ChannelResource, '/channels/<int:channel_id>', endpoint='channels')
api.add_resource(ChannelStatsResource, '/channels/<int:channel_id>/stats/<string:period>')
api.add_resource(DeviceResource, '/devices')
api.add_resource(DeviceResource, '/devices/<int:device_id>', endpoint='devices')
api.add_resource(EntryResource, '/updates')

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
def device_details(device_id: int):
    device_data = DeviceResource().get(device_id)['data']

    return render_template('device_details.html', device=device_data)


@app.route('/channel/<int:channel_id>')
def channel_details(channel_id: int):
    channel_data = ChannelResource().get(channel_id)['data']

    return render_template('channel_details.html', channel=channel_data)
