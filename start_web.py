from flask import Flask

app = Flask(__name__, static_folder='web/dist')


@app.route('/', defaults=dict(p='index.html'))
@app.route('/<path:p>')
def serve_static(p):
    return app.send_static_file(p)


if __name__ == '__main__':
    app.run(debug=True)
