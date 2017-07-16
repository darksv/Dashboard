import sys
sys.path.append('app')
import config
from api import app

if __name__ == '__main__':
    app.run(debug=config.DEVELOPMENT, host=config.HOST)
