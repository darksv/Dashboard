from app.db import DB
from app.db.api import entries as Readings, sensors as Sensors
from app.util import localize_datetime
from flask_restful import Resource


class SensorResource(Resource):
    def get(self, sensor_id=None):
        multiple = sensor_id is None

        if multiple:
            sensors = Sensors.get_all_sensors(DB)
        else:
            sensors = [Sensors.get_sensor(DB, sensor_id)]

        data = []

        for sensor in sensors:
            if sensor is None:
                continue

            sensor_data = sensor._asdict()

            reading = Readings.get_last_entry(DB, sensor.id)
            if reading is not None:
                last_update = localize_datetime(reading.timestamp).isoformat()
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
