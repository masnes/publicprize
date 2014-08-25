# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.
import flask
import publicprize.controller as ppc

class Contest(ppc.Task):
    def action_contestants(biv_obj):
        return flask.render_template("contest/contestants.html")
    def action_about(biv_obj):
        return flask.render_template("contest/about.html")
    def action_donors(biv_obj):
        return flask.render_template("contest/donors.html")

class Contestant(ppc.Task):
    pass
    
class Founder(ppc.Task):
    pass
