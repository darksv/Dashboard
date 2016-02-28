import sys
from flask import Flask
from flask_restful import Resource, Api, reqparse
from lib.db import Database
from lib.db.api import sensors as Sensors, readings as Readings

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
        sensor = Sensors.get_sensor(db, sensor_id)
        if sensor is None:
            return {}

        return sensor._asdict()

    def put(self, sensor_id):
        return {'sensor': sensor_id}


class SensorListResource(Resource):
    def get(self):
        return {a: b for a, b in enumerate(range(0, 100))}


class ReadingResource(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('internal_id', type=str)
        parser.add_argument('sensor_id', type=int)
        parser.add_argument('value', type=float)
        args = parser.parse_args()

        sensor_id = args['sensor_id']
        if sensor_id is None:
            internal_id = args['internal_id']

            sensor = Sensors.get_sensor_by_internal_id(db, internal_id)
            if sensor is None:
                sensor = Sensors.create_sensor(db, internal_id=internal_id, sensor_type=1)

            sensor_id = sensor.id

        reading = Readings.create_reading(db, sensor_id=sensor_id, value=args['value'])
        data = reading._asdict()
        data['timestamp'] = reading.timestamp.timestamp()

        return data

api.add_resource(SensorRegisterResource, '/sensor/register')
api.add_resource(SensorResource, '/sensor/<int:sensor_id>')
api.add_resource(SensorListResource, '/sensors')
api.add_resource(ReadingResource, '/reading')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = None

    app.run(debug=True, host=host)
