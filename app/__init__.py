from flask import Flask

app = Flask('dashboard', static_folder='app/static', template_folder='app/templates')
