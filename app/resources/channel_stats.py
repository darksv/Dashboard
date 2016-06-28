from flask_restful import Resource
from app.db import DB
from app.db.channels import get_recent_channel_stats, get_daily_channel_stats, get_monthly_channel_stats
from app.util import localize_datetime


class ChannelStatsResource(Resource):
    def get(self, channel_id, period):
        data = []

        if period == 'recent':
            data = []
            for timestamp, value in get_recent_channel_stats(DB, channel_id, 100):
                data.append((localize_datetime(timestamp).isoformat(), value))

        elif period == 'daily':
            data = get_daily_channel_stats(DB, channel_id)
        elif period == 'monthly':
            data = get_monthly_channel_stats(DB, channel_id)

        return dict(success=True, data=data, message=None)
