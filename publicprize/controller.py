# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import flask
from publicprize import app

@app.route("/")
@app.route("/index.html")
def home_page():
    return flask.render_template("index.html")

@app.route('/<biv_id>/contestants')
def contestants(biv_id):
    return flask.render_template("contest/contestants.html")

@app.errorhandler(404)
def page_not_found(e):
    return flask.render_template('error/not-found.html'), 404
