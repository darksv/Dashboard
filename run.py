import sys
import config
from app import app

if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = None

    app.run(debug=config.DEVELOPMENT, host=host)
