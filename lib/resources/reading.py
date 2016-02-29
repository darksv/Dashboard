from lib.db import DB
from lib.db.api import readings as Readings, sensors as Sensors
from flask import request
from flask_restful import Resource


class ReadingResource(Resource):
    def put(self):
        args = request.get_json()

        sensor_id = args.get('sensor_id', None)
        if sensor_id is None:
            internal_id = args['internal_id']

            sensor = Sensors.get_sensor_by_internal_id(DB, internal_id)
            if sensor is None:
                sensor = Sensors.create_sensor(DB, internal_id=internal_id, sensor_type=1)

            sensor_id = sensor.id

        reading = Readings.create_reading(DB, sensor_id=sensor_id, value=args['value'])
        data = reading._asdict()
        data['timestamp'] = reading.timestamp.timestamp()

        return data
