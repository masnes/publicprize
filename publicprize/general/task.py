# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.
import flask
import publicprize.controller as ppc

class General(ppc.Task):
    PERMISSIONS = {
        'index': 'ANYBODY',
        '': 'ANYBODY',
        }
    def action_index(biv_obj):
        return flask.render_template("general/index.html")
    
    def action_not_found(biv_obj):
        return flask.render_template('general/not-found.html'), 404
        return ppc.return_value({
            'template': 'general/not-found.html',
            'status_code': 'NOT_FOUND'})