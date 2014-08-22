# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import flask
app = flask.Flask(__name__)
app.config.from_object('config.DevConfig')

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
