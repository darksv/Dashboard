from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


class SensorResource(Resource):
    def get(self, sensor_id):
        return {'sensor': sensor_id}

    def put(self, sensor_id):
        return {'sensor': sensor_id}

api.add_resource(SensorResource, '/api/sensor/<sensor_id>')

if __name__ == '__main__':
    app.run()
