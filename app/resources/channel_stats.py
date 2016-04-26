from app.db import DB
from app.db.channels import get_daily_channel_stats, get_monthly_channel_stats
from flask_restful import Resource


class ChannelStatsResource(Resource):
    def get(self, channel_id, period):
        data = []

        if period == 'daily':
            data = get_daily_channel_stats(DB, channel_id)
        elif period == 'monthly':
            data = get_monthly_channel_stats(DB, channel_id)

        return dict(success=True, data=data, message=None)
