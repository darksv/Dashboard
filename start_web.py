from flask import Flask, render_template

app = Flask(__name__, static_folder='web/dist', static_url_path='', template_folder='app/templates')


@app.route('/')
def index():
    return render_template('web/dist/index.html')


@app.route('/<path:p>')
def _static(p):
    return app.send_static_file(p)


if __name__ == '__main__':
    app.run(debug=True)
