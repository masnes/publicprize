# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import flask
from flask.ext.wtf import Form
import publicprize.auth.model as pam
import publicprize.contest.model as pcm
from publicprize import controller
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

class ContestantForm(Form):
    display_name = StringField('Project Name', validators=[DataRequired()])
    contestant_desc = TextAreaField('Project Summary', validators=[DataRequired()])
    youtube_code = StringField(
        'YouTube Video Code',
        validators=[DataRequired()]
    )
    slideshow_code = StringField(
        'SlideShare Pitch Deck Code',
        validators=[DataRequired()]
    )
    founder_desc = StringField('Founder Short Bio', validators=[DataRequired()])
    website = StringField('Project Website')

    def execute(self, contest):
        if self.is_submitted() and self.validate():
            c = self._update_models(contest)
            if c:
                return flask.redirect(c.format_uri('contestant'))
        return flask.render_template(
            'contest/submit.html',
            contest=contest,
            form=self
        )
        
    def validate_and_execute(self, contest):
        if self.validate_on_submit():
            return form
        return False

    def _update_models(self, contest):
        c = pcm.Contestant()
        self.populate_obj(c)
        f = pcm.Founder()
        self.populate_obj(f)
        f.display_name = flask.session['user.display_name']
        controller.db.session.add(c)
        controller.db.session.add(f)
        controller.db.session.flush()
        controller.db.session.add(
            pam.BivAccess(
                source_biv_id=contest.biv_id,
                target_biv_id=c.biv_id
            )
        )
        controller.db.session.add(
            pam.BivAccess(
                source_biv_id=c.biv_id,
                target_biv_id=f.biv_id
            )
        )
        return c
