# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.
import flask
import publicprize.controller as ppc

class Contest(ppc.Task):
    def action_contestants(biv_obj):
        return flask.render_template("contest/contestants.html")

class Contestant(ppc.Task):
    pass
    
class Founder(ppc.Task):
    pass
