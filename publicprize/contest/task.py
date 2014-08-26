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
        return flask.render_template(
            "contest/contestants.html",
            contest=biv_obj,
            selected='contestants',
            contestants=pcm.Contestant.query.select_from(pam.BivAccess).filter(
                pam.BivAccess.source_biv_id == biv_obj.biv_id,
                pam.BivAccess.target_biv_id == pcm.Contestant.biv_id
            ).all()
        )
    def action_contestant(biv_obj):
        # TODO(pjm): need standard query arg access
        contestant_id = flask.request.args.get('t')
        # TODO(pjm): BivAccess should be automated - ie. load contestant
        # within contest's realm
        Contest._verify_access(biv_obj, contestant_id)
        return flask.render_template(
            'contest/detail.html',
            contest=biv_obj,
            contestant=pcm.Contestant.query.filter_by(
                biv_id=contestant_id).first_or_404(),
            founders=pcm.Founder.query.select_from(pam.BivAccess).filter(
                pam.BivAccess.source_biv_id == contestant_id,
                pam.BivAccess.target_biv_id == pcm.Founder.biv_id
            ).all()
        )
    def action_donors(biv_obj):
        return Contest._render_template(biv_obj, 'donors')
    def action_founder_avatar(biv_obj):
        founder_id = flask.request.args.get('t')
        Contest._verify_access(biv_obj, founder_id)
        founder = pcm.Founder.query.filter_by(
            biv_id=founder_id).first_or_404()
        # TODO(pjm): share code with action_logo()
        return flask.send_file(
            io.BytesIO(founder.founder_avatar),
            'image/' + founder.avatar_type
        )
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
    def _verify_access(biv_obj, target_biv_id):
        pam.BivAccess.query.filter_by(
            source_biv_id=biv_obj.biv_id,
            target_biv_id=target_biv_id
        ).first_or_404()
        

class Contestant(ppc.Task):
    pass
    
class Founder(ppc.Task):
    pass
