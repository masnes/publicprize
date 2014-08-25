# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import flask
import flask.ext.sqlalchemy as fesa
import publicprize.config as ppc

_app = flask.Flask(__name__, template_folder=".")
_app.config.from_object(ppc.DevConfig)

db = fesa.SQLAlchemy(_app)

def app():
    return _app

@_app.route("/<path:path>")
def route(path):
    print(path)
    return flask.render_template("site_root/index.html")


@_app.route("/")
@_app.route("/index.html")
def home_page():
    return flask.render_template("site_root/index.html")

@_app.route('/<biv_id>/contestants')
def contestants(biv_id):
    return flask.render_template("contest/contestants.html")

@_app.route('/<biv_id>/donors')
def donors(biv_id):
    return flask.render_template("contest/donors.html")

@_app.route('/<biv_id>/about')
def about(biv_id):
    return flask.render_template("contest/about.html")

@_app.route('/<biv_id>/how-to-enter')
def how_to_enter(biv_id):
    return flask.render_template("contest/how-to-enter.html")

@_app.errorhandler(404)
def page_not_found(e):
    return flask.render_template('error/not-found.html'), 404
