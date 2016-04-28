import config
import requests
import iso8601
import collections
import json
from flask import render_template, send_from_directory, jsonify
from app import app
from app.utils import convert_in_dict

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
    devices = requests.get('http://test.hsdxd.usermd.net/devices').json()['data']

    for device in devices:
        for channel in device['channels']:
            convert_in_dict(channel, 'value_updated', iso8601.parse_date)

    return render_template('devices.html', title='Dashboard', devices=devices)


@app.route('/api/<path:path>')
def api_redirect(path: str):
    result = requests.get('http://test.hsdxd.usermd.net/' + path).json()
    return jsonify(result)


@app.route('/device/<int:device_id>')
def device_details(device_id: int):
    device_data = requests.get('http://test.hsdxd.usermd.net/devices/{0}'.format(device_id)).json()['data']

    return render_template('device_details.html', title='Urządzenie #' + str(device_id), device=device_data)


@app.route('/channel/<int:channel_id>')
def channel_details(channel_id: int):
    channel_data = requests.get('http://test.hsdxd.usermd.net/channels/{0}'.format(channel_id)).json()['data']
    convert_in_dict(channel_data, 'value_updated', iso8601.parse_date)

    return render_template('channel_details.html', title='Kanał #' + str(channel_id), channel=channel_data)

if __name__ == '__main__':
    app.run(debug=config.DEVELOPMENT, host=config.HOST)
