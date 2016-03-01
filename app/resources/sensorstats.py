from app.db import DB
from app.db.api import readings as Readings, sensors as Sensors
from app.util import localize_datetime
from flask_restful import Resource


class SensorStatsResource(Resource):
    def get(self, sensor_id, period):
        return dict(success=True, data={}, message=None)
