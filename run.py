import config
import requests
from flask import render_template, send_from_directory
from app import app


if config.DEVELOPMENT:
    @app.route('/css/<path:path>')
    def send_css(path: str):
        return send_from_directory('app/static/css', path)


    @app.route('/js/<path:path>')
    def send_js(path: str):
        return send_from_directory('app/static/js', path)


@app.route('/')
def hello_world():
    result = requests.get('http://test.hsdxd.usermd.net/sensors')

    return render_template('index.html', title='Dashboard', sensors=result.json()['data'])

if __name__ == '__main__':
    app.run(debug=config.DEVELOPMENT)
