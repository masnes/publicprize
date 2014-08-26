# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.
import flask
import io
import publicprize.contest.model as pcm
import publicprize.controller as ppc
import publicprize.auth.model as pam

class Contest(ppc.Task):
    def action_about(biv_obj):
        return Contest._render_template(biv_obj, 'about')
    def action_contestants(biv_obj):
        return Contest._render_template(
            biv_obj,
            'contestants',
            contestants=pcm.Contestant.query.select_from(pam.BivAccess).filter(
                pam.BivAccess.source_biv_id == biv_obj.biv_id,
                pam.BivAccess.target_biv_id == pcm.Contestant.biv_id
            ).all()
        )
    def action_donors(biv_obj):
        return Contest._render_template(biv_obj, 'donors')
    def action_how_to_enter(biv_obj):
        return Contest._render_template(biv_obj, 'how-to-enter')
    def action_index(biv_obj):
        return Contest.action_contestants(biv_obj)
    def action_logo(biv_obj):
        return flask.send_file(
            io.BytesIO(biv_obj.contest_logo),
            'image/' + biv_obj.logo_type
        )
    def _render_template(biv_obj, name, **kwargs):
        return flask.render_template(
            "contest/" + name + ".html",
            contest=biv_obj,
            selected=name,
            **kwargs
        )

class Contestant(ppc.Task):
    def action_contestant(biv_obj):
        return flask.render_template(
            'contest/detail.html',
            contest=pcm.Contest.query.select_from(pam.BivAccess).filter(
                pam.BivAccess.target_biv_id == biv_obj.biv_id
            ).first_or_404(),
            contestant=biv_obj,
            founders=pcm.Founder.query.select_from(pam.BivAccess).filter(
                pam.BivAccess.source_biv_id == biv_obj.biv_id,
                pam.BivAccess.target_biv_id == pcm.Founder.biv_id
            ).all()
        )
    def action_index(biv_obj):
        return Contestant.action_contestant(biv_obj)
    
class Founder(ppc.Task):
    def action_founder_avatar(biv_obj):
        return flask.send_file(
            io.BytesIO(biv_obj.founder_avatar),
            'image/' + biv_obj.avatar_type
        )
