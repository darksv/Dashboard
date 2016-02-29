import sys
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from lib.db import Database
from lib.db.api import sensors as Sensors, readings as Readings

app = Flask(__name__)
api = Api(app)
db = Database('')


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
    def get(self, sensor_id=None):
        multiple = sensor_id is None

        if multiple:
            sensors = Sensors.get_all_sensors(db)
        else:
            sensors = [Sensors.get_sensor(db, sensor_id)]

        data = []

        for sensor in sensors:
            if sensor is None:
                continue

            sensor_data = sensor._asdict()

            reading = Readings.get_last_reading(db, sensor.id)
            if reading is not None:
                last_update = reading.timestamp.timestamp()
                last_value = reading.value
            else:
                last_update = None
                last_value = None

            sensor_data['updated'] = last_update
            sensor_data['value'] = last_value

            data.append(sensor_data)

        if len(data) == 0:
            return {}

        if not multiple:
            data = data[0]

        return dict(success=True, data=data, message=None)

    def put(self, sensor_id):
        return {'sensor': sensor_id}


class ReadingResource(Resource):
    def put(self):
        args = request.get_json()

        sensor_id = args.get('sensor_id', None)
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

# api.add_resource(SensorRegisterResource, '/sensors/register')
api.add_resource(SensorResource, '/sensors')
api.add_resource(SensorResource, '/sensors/<int:sensor_id>', endpoint='sensors')
api.add_resource(ReadingResource, '/readings')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = None

    app.run(debug=True, host=host)
