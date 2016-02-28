from flask import Flask
from flask_restful import Resource, Api, reqparse
from lib.db import Database
from lib.db.api import sensors as Sensors

app = Flask(__name__)
api = Api(app)
db = Database('mysql+pymysql://XXX:bUZ2so3KmBn43GqaIo1W@mysql8.mydevil.net/XXX')


class SensorRegisterResource(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('internal_id', type=str)
        parser.add_argument('type', type=int)
        args = parser.parse_args()

        sensor = Sensors.get_sensor_by_internal_id(db, args['internal_id'])
        if sensor is None:
            sensor = Sensors.create_sensor(db, args['internal_id'], args['type'])

        return sensor._asdict()


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

api.add_resource(SensorRegisterResource, '/sensor/register')
api.add_resource(SensorResource, '/sensor/<int:sensor_id>')
api.add_resource(SensorListResource, '/sensors')
api.add_resource(ReadingResource, '/reading')

if __name__ == '__main__':
    app.run(debug=True)
