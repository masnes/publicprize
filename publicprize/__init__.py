# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import flask.ext.sqlalchemy
import publicprize.config

app = flask.Flask(__name__, template_folder=".")
app.config.from_object(publicprize.config.DevConfig)
db = flask.ext.sqlalchemy.SQLAlchemy(app)

import publicprize.controller
