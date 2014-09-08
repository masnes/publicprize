# -*- coding: utf-8 -*-
""" controller actions for Contest, Contestand and Founder

    :copyright: Copyright (c) 2014 Bivio Software, Inc.  All Rights Reserved.
    :license: Apache, see LICENSE for more details.
"""

import flask
import io
import publicprize.contest.form as pcf
import publicprize.contest.model as pcm
import publicprize.controller as ppc
import publicprize.auth.model as pam

class Contest(ppc.Task):
    """Contest actions"""
    def action_about(biv_obj):
        """About page"""
        return Contest._render_template(biv_obj, 'about')
    def action_contestants(biv_obj):
        """Public contestant list"""
        return Contest._render_template(
            biv_obj,
            'contestants',
            contestants=pcm.Contestant.query.select_from(pam.BivAccess).filter(
                pam.BivAccess.source_biv_id == biv_obj.biv_id,
                pam.BivAccess.target_biv_id == pcm.Contestant.biv_id
            ).filter(pcm.Contestant.is_public == True).all()
        )
    def action_donors(biv_obj):
        """Donors page"""
        return Contest._render_template(biv_obj, 'donors')
    def action_how_to_enter(biv_obj):
        """How-to-Enter page"""
        return Contest._render_template(biv_obj, 'how-to-enter')
    def action_index(biv_obj):
        """Default to contestant list"""
        return Contest.action_contestants(biv_obj)
    def action_logo(biv_obj):
        """Contestant logo image"""
        return flask.send_file(
            io.BytesIO(biv_obj.contest_logo),
            'image/' + biv_obj.logo_type
        )
    @ppc.login_required
    def action_submit_contestant(biv_obj):
        """Submit project page"""
        return pcf.ContestantForm().execute(biv_obj)
    def _render_template(biv_obj, name, **kwargs):
        """Render the page, putting the selected menu and contest in env"""
        return flask.render_template(
            "contest/" + name + ".html",
            contest=biv_obj,
            selected=name,
            **kwargs
        )

class Contestant(ppc.Task):
    """Contestant actions"""
    def action_contestant(biv_obj):
        """Project detail page, loads contest owner and project founders"""
        return Contestant._render_template(biv_obj, 'detail',
            founders=pcm.Founder.query.select_from(pam.BivAccess).filter(
                pam.BivAccess.source_biv_id == biv_obj.biv_id,
                pam.BivAccess.target_biv_id == pcm.Founder.biv_id
            ).all()
        )
    def action_donate(biv_obj):
        """Donation form"""
        return pcf.DonateForm().execute(biv_obj)
    def action_donate_cancel(biv_obj):
        form = pcf.DonateForm()
        form.amount.errors = ["Please resubmit your donation."]
        return form.execute(biv_obj)
    def action_donate_confirm(biv_obj):
        """Confirm donation"""
        return pcf.DonateConfirmForm().execute(biv_obj)
    def action_index(biv_obj):
        """Default to contestant page"""
        return Contestant.action_contestant(biv_obj)
    def _render_template(biv_obj, name, **kwargs):
        return flask.render_template(
            "contest/" + name + ".html",
            contestant=biv_obj,
            contest=biv_obj.get_contest(),
            **kwargs
        )
    
class Founder(ppc.Task):
    """Founder actions"""
    def action_founder_avatar(biv_obj):
        """Founder avatar image"""
        return flask.send_file(
            io.BytesIO(biv_obj.founder_avatar),
            'image/' + biv_obj.avatar_type
        )
