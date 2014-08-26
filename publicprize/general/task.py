# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

from publicprize import controller
import flask

class General(controller.Task):
    def action_index(biv_obj):
        return flask.render_template("general/index.html")
    
    def action_not_found(biv_obj):
        return flask.render_template('general/not-found.html'), 404
