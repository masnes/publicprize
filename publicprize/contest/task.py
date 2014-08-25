# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.
import flask
import io
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
        return flask.send_file(
            io.BytesIO(biv_obj.contest_logo),
            'image/' + biv_obj.logo_type
        )
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
