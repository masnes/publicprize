# -*- coding: utf-8 -*-
""" controller actions for Contest, Contestand and Founder

    :copyright: Copyright (c) 2014 Bivio Software, Inc.  All Rights Reserved.
    :license: Apache, see LICENSE for more details.
"""

import io
import random

import functools
import flask
import sqlalchemy.orm
import werkzeug.exceptions

from . import form as pcf
from . import model as pcm
from .. import common
from .. import controller as ppc
from .. import inspect as ppi
from ..auth import model as pam

_template = common.Template('evc');

def user_is_admin(func):
    """Require the current user is an administrator."""
    @functools.wraps(func)
    def decorated_function(*args, **kwargs):
        """Forbidden unless allowed."""
        if pam.Admin.is_admin():
            return func(*args, **kwargs)
        werkzeug.exceptions.abort(403)
    return decorated_function


def user_is_contestant_founder_or_admin(func):
    """Require the current user is the contestant founder for an expired
    contest or an administrator."""
    @functools.wraps(func)
    def decorated_function(*args, **kwargs):
        """Forbidden unless allowed."""
        contestant = args[0]
        if pam.Admin.is_admin() or (contestant.is_founder() \
            and contestant.get_contest().is_expired() \
            and contestant.get_contest().is_scoring_completed):
            return func(*args, **kwargs)
        werkzeug.exceptions.abort(403)
    return decorated_function


def user_is_judge(func):
    """Require the current user is a contest judge."""
    @functools.wraps(func)
    def decorated_function(*args, **kwargs):
        """Forbidden unless allowed."""
        if args[0].is_judge():
            return func(*args, **kwargs)
        werkzeug.exceptions.abort(403)
    return decorated_function


class Contest(ppc.Task):
    """Contest actions"""
    def action_about(biv_obj):
        """About page"""
        return _template.render_template(biv_obj, 'about')

    @ppc.login_required
    @user_is_admin
    def action_admin(biv_obj):
        """Contest administration"""
        return _template.render_template(biv_obj, 'admin')

    def action_contestants(biv_obj):
        """Public contestant list"""
        return _template.render_template(
            biv_obj,
            'contestants',
            contest_url=biv_obj.format_absolute_uri(),
        )

    def action_index(biv_obj):
        """Default to contestant list"""
        return Contest.action_contestants(biv_obj)

    def action_judges(biv_obj):
        """List of judges page"""
        return _template.render_template(biv_obj, 'judges')

    @ppc.login_required
    @user_is_judge
    def action_judging(biv_obj):
        """List of contestants for judgement"""
        return _template.render_template(
            biv_obj,
            'judging',
        )

    def action_logo(biv_obj):
        """Contestant logo image"""
        return flask.send_file(
            io.BytesIO(biv_obj.contest_logo),
            'image/{}'.format(biv_obj.logo_type)
        )

    def action_new_test_judge(biv_obj):
        """Creates a new test user and judge models and log in."""
        # will raise an exception unless TEST_USER is configured
        flask.g.pub_obj.task_class().action_new_test_user()
        judge = pcm.Judge()
        pcm.db.session.add(judge)
        pcm.db.session.flush()
        pam.db.session.add(pam.BivAccess(
            source_biv_id=flask.session['user.biv_id'],
            target_biv_id=judge.biv_id
        ))
        pam.db.session.add(pam.BivAccess(
            source_biv_id=biv_obj.biv_id,
            target_biv_id=judge.biv_id
        ))
        return flask.redirect('/')

    def action_rules(biv_obj):
        return flask.redirect('/static/pdf/rules.pdf')

    @ppc.login_required
    def action_submit_contestant(biv_obj):
        """Submit project page"""
        return pcf.Contestant().execute(biv_obj)

    def get_template():
        return _template;


class Contestant(ppc.Task):
    """Contestant actions"""
    def action_contestant(biv_obj):
        """Project detail page, loads contest owner and project founders"""
        if biv_obj.is_public or biv_obj.is_under_review:
            if biv_obj.get_contest().is_expired():
                # TODO(pjm): share return value with Donate form
                return _template.render_template(
                    biv_obj.get_contest(),
                    'detail',
                    contestant=biv_obj,
                    contestant_url=biv_obj.format_absolute_uri(),
                    contestant_tweet=biv_obj.display_name
                )
            return pcf.Donate().execute(biv_obj)
        werkzeug.exceptions.abort(404)

    def action_donate_cancel(biv_obj):
        """Return from cancelled payment on paypal site"""
        donor = pcm.Donor.unsafe_load_from_session()
        if donor:
            donor.remove_from_session()
            donor.donor_state = 'canceled'
            ppc.db.session.add(donor)
        form = pcf.Donate()
        form.amount.errors = ['Please resubmit your donation.']
        return form.execute(biv_obj)

    def action_donate_done(biv_obj):
        """Execute the payment after returning from paypal"""
        return pcf.Donate().execute_payment(biv_obj)

    def action_index(biv_obj):
        """Default to contestant page"""
        return Contestant.action_contestant(biv_obj)

    @ppc.login_required
    @user_is_judge
    def action_judging(biv_obj):
        """Contestant judgement"""
        return pcf.Judgement().execute(biv_obj)

    @ppc.login_required
    @user_is_contestant_founder_or_admin
    def action_score(biv_obj):
        """Show the score report for the contestant."""
        summary = {
            'amount_score': 0,
            'amount_raised': 0,
            'judge_score': 0,
            'total_score': 0
        }
        for row in biv_obj.get_contest().get_admin_contestants():
            if row['contestant'].biv_id == biv_obj.biv_id:
                summary = row
                break
        scores_by_judge = biv_obj.get_completed_judge_scores()
        judges = []
        for user_id in scores_by_judge.keys():
            judges.append(
                {
                    'biv_id': user_id,
                    'display_name': pam.User.query.filter_by(
                        biv_id=user_id).one().display_name,
                    'general_comment': pcm.JudgeScore.query.filter_by(
                        judge_biv_id=user_id,
                        question_number=0
                     ).first().judge_comment,
                    'judge_total': biv_obj._score_rows(scores_by_judge[user_id])
                }
            )
        random.Random(biv_obj.display_name).shuffle(judges)
        return _template.render_template(
            biv_obj.get_contest(),
            'score',
            contestant=biv_obj,
            judges=judges,
            scores_by_judge=scores_by_judge,
            summary=summary
        )

    def action_thank_you(biv_obj):
        """Show a Thank you page with social media links for contestant."""
        return _template.render_template(
            biv_obj.get_contest(),
            'thank-you',
            sub_base_template=_template.base_template('detail'),
            contestant=biv_obj,
            contestant_url=biv_obj.format_absolute_uri(),
            contestant_tweet="I just backed " + biv_obj.display_name
        )


class Founder(ppc.Task):
    """Founder actions"""
    def action_founder_avatar(biv_obj):
        """Founder avatar image"""
        return flask.send_file(
            io.BytesIO(biv_obj.founder_avatar),
            'image/{}'.format(biv_obj.avatar_type)
        )
