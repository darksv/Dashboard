from flask import Flask, request
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)


class SensorResource(Resource):
    def get(self, sensor_id):
        return {'sensor': sensor_id}

    def put(self, sensor_id):
        return {'sensor': sensor_id}


class SensorListResource(Resource):
    def get(self):
        return {a: b for a, b in enumerate(range(0, 100))}


class ReadingResource(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('sensor', type=str)
        parser.add_argument('value', type=float)

        return parser.parse_args()


api.add_resource(SensorListResource, '/api/sensors')
api.add_resource(SensorResource, '/api/sensor/<sensor_id>')
api.add_resource(ReadingResource, '/api/reading')

if __name__ == '__main__':
    app.run(debug=True)
