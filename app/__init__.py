from flask import Flask
from flask_restful import Api
from app.resources.channel import ChannelResource
from app.resources.channel_stats import ChannelStatsResource
from app.resources.device import DeviceResource
from app.resources.entry import EntryResource


app = Flask(__name__)

api = Api(app)
api.add_resource(ChannelResource, '/channels')
api.add_resource(ChannelResource, '/channels/<int:channel_id>', endpoint='channels')
api.add_resource(ChannelStatsResource, '/channels/<int:channel_id>/stats/<string:period>')
api.add_resource(DeviceResource, '/devices')
api.add_resource(DeviceResource, '/devices/<int:device_id>', endpoint='devices')
api.add_resource(EntryResource, '/updates')
