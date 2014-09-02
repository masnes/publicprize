# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import flask
from flask.ext.wtf import Form
import publicprize.auth.model as pam
import publicprize.contest.model as pcm
from publicprize import controller
import re
import urllib.request
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

class ContestantForm(Form):
    display_name = StringField('Project Name', validators=[DataRequired()])
    contestant_desc = TextAreaField(
        'Project Summary', validators=[DataRequired()])
    youtube_code = StringField(
        'YouTube Video URL',
        validators=[DataRequired()]
    )
    slideshow_code = StringField(
        'SlideShare Pitch Deck URL',
        validators=[DataRequired()]
    )
    founder_desc = StringField(
        'Founder Short Bio', validators=[DataRequired()])
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

    def validate(self):
        if super().validate():
            self._validate_youtube()
            self._validate_slideshare()
            self._validate_website()
            if not self.errors:
                return True
        return False

    def _slideshare_code(self):
        # www.slideshare.net/benjaminevans/culture-kitchen-pitch-deck-18074260
        # www.slideshare.net/slideshow/embed_code/18074260
        value = self.slideshow_code.data
        m = re.search('(\d{5}\d+)$', value)
        if m:
            return m.group(1)
        return None
        
    def _update_models(self, contest):
        self.youtube_code.data = self._youtube_code()
        self.slideshow_code.data = self._slideshare_code()
        c = pcm.Contestant()
        self.populate_obj(c)
        c.is_public = controller.app().config['PP_ALL_PUBLIC_CONTESTANTS']
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

    def _youtube_code(self):
        value = self.youtube_code.data
        # http://youtu.be/a1Y73sPHKxw
        # or https://www.youtube.com/watch?v=a1Y73sPHKxw
        if re.search('\?', value) and re.search('v\=', value):
            m = re.search(r'(?:\?|\&)v\=(.*)', value)
            if m:
                return m.group(1)
        else:
            m = re.search(r'\/([^\&\?\/]+)$', value)
            if m:
                return m.group(1)
        return None

    def _validate_url(self, url):
        if not re.search(r'^http', url):
            url = 'http://' + url
        try:
            req = urllib.request.urlopen(url, None, 10)
            req.read()
            req.close()
        except urllib.request.URLError:
            return False
        except ValueError:
            return False
        return True

    def _validate_website(self):
        if self.website.data:
            if not self._validate_url(self.website.data):
                self.website.errors = ['Website invalid or unavailable']

    def _validate_youtube(self):
        code = self._youtube_code()
        if code:
            if not self._validate_url('http://youtu.be/' + code):
                self.youtube_code.errors = [
                    'Unknown YouTube VIDEO_ID: ' + code]
        else:
            self.youtube_code.errors = ['Invalid YouTube URL']

    def _validate_slideshare(self):
        code = self._slideshare_code()
        if code:
            if not self._validate_url(
                'http://www.slideshare.net/slideshow/embed_code/' + code):
                self.slideshow_code.errors = ['Unknown SlideShare ID: ' + code]
        else:
            self.slideshow_code.errors = ['Invalid SlideShare URL']
