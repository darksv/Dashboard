from flask import Flask
from flask_restful import Api
from app.resources.sensor import SensorResource
from app.resources.sensorstats import SensorStatsResource
from app.resources.entry import EntryResource

app = Flask(__name__)

api = Api(app)
api.add_resource(SensorResource, '/sensors')
api.add_resource(SensorResource, '/sensors/<int:sensor_id>', endpoint='sensors')
api.add_resource(SensorStatsResource, '/sensors/<int:sensor_id>/stats/<string:period>')
api.add_resource(EntryResource, '/updates')
