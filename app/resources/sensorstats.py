from app.db import DB
from app.db.api import stats as Stats
from flask_restful import Resource


class SensorStatsResource(Resource):
    def get(self, sensor_id, period):
        data = Stats.get_daily_stats(DB, sensor_id)

        return dict(success=True, data=data, message=None)
