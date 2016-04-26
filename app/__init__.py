from flask import Flask
from flask_restful import Api
from app.resources.channel import ChannelResource
from app.resources.channel_stats import ChannelStatsResource
from app.resources.entry import EntryResource

app = Flask(__name__)

api = Api(app)
api.add_resource(ChannelResource, '/sensors')
api.add_resource(ChannelResource, '/sensors/<int:channel_id>', endpoint='sensors')
api.add_resource(ChannelStatsResource, '/sensors/<int:channel_id>/stats/<string:period>')
api.add_resource(EntryResource, '/updates')
