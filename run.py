from flask import render_template, send_from_directory
from app import app


@app.route('/css/<path:path>')
def send_css(path: str):
    return send_from_directory('app/static/css', path)


@app.route('/js/<path:path>')
def send_js(path: str):
    return send_from_directory('app/static/js', path)


@app.route('/')
def hello_world():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
