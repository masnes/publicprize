# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import flask
from publicprize import app
@app.route("/")
@app.route("/index.html")
def home_page():
    return flask.render_template("site_root/index.html")

@app.route('/<biv_id>/contestants')
def contestants(biv_id):
    return flask.render_template("contest/contestants.html")

@app.route('/<biv_id>/donors')
def donors(biv_id):
    return flask.render_template("contest/donors.html")

@app.route('/<biv_id>/about')
def about(biv_id):
    return flask.render_template("contest/about.html")

@app.route('/<biv_id>/how-to-enter')
def how_to_enter(biv_id):
    return flask.render_template("contest/how-to-enter.html")

@app.errorhandler(404)
def page_not_found(e):
    return flask.render_template('error/not-found.html'), 404
