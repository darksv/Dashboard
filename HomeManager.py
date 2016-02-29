import sys
from flask import Flask
from flask_restful import Api
from lib.resources.sensor import SensorResource
from lib.resources.reading import ReadingResource

app = Flask(__name__)

api = Api(app)
api.add_resource(SensorResource, '/sensors')
api.add_resource(SensorResource, '/sensors/<int:sensor_id>', endpoint='sensors')
api.add_resource(ReadingResource, '/readings')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = None

    app.run(debug=True, host=host)
