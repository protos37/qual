# -*- encoding:utf-8 -*-
from flask import Flask
from qual.views.frontend import frontend

app = Flask(__name__)
app.register_blueprint(frontend, url_prefix='')
