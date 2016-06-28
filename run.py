import config
from app import app
from client import start_client

if __name__ == '__main__':
    start_client(in_background=True)
    app.run(debug=config.DEVELOPMENT, host=config.HOST)
