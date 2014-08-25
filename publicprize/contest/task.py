# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.
import flask
import publicprize.controller as ppc

class Contest(ppc.Task):
    def action_contestants(biv_obj):
        return Contest._render_template(biv_obj, 'contestants')
    def action_about(biv_obj):
        return Contest._render_template(biv_obj, 'about')
    def action_donors(biv_obj):
        return Contest._render_template(biv_obj, 'donors')
    def action_how_to_enter(biv_obj):
        return Contest._render_template(biv_obj, 'how-to-enter')
    def action_logo(biv_obj):
        # TODO(pjm): see if an easier way - also use logo_type
        response = flask.make_response(biv_obj.contest_logo)
        response.headers['Content-Type'] = 'image/gif'
        response.headers['Content-DIsposition'] = 'attachment; filename=logo.gif'
        return response
    def _render_template(biv_obj, name):
        return flask.render_template(
            "contest/" + name + ".html",
            contest=biv_obj,
            selected=name
        )

class Contestant(ppc.Task):
    pass
    
class Founder(ppc.Task):
    pass
