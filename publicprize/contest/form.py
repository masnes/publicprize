# -*- coding: utf-8 -*-
""" contest forms: HTTP form processing for contest pages

    :copyright: Copyright (c) 2014 Bivio Software, Inc.  All Rights Reserved.
    :license: Apache, see LICENSE for more details.
"""

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
    """Project submission form.

    Fields:
        display_name: project name
        contestant_desc: project summary
        youtube_url: full YouTube video url
        slideshow_url: full SlideShare url
        founder_desc: current user's founder info for this project
        website: project website (optional)
    """
    display_name = StringField('Project Name', validators=[DataRequired()])
    contestant_desc = TextAreaField(
        'Project Summary', validators=[DataRequired()])
    youtube_url = StringField(
        'YouTube Video URL',
        validators=[DataRequired()]
    )
    slideshow_url = StringField(
        'SlideShare Pitch Deck URL',
        validators=[DataRequired()]
    )
    founder_desc = StringField(
        'Founder Short Bio', validators=[DataRequired()])
    website = StringField('Project Website')

    def execute(self, contest):
        """Validates and creates the contestant model"""
        if self.is_submitted() and self.validate():
            contestant = self._update_models(contest)
            if contestant:
                flask.flash('Thank you for submitting your entry. You will be contacted by email when your entry has been reviewed.')
                return flask.redirect(contestant.format_uri('contestant'))
        return flask.render_template(
            'contest/submit.html',
            contest=contest,
            form=self
        )

    def validate(self):
        """Performs superclass wtforms validation followed by url
        field validation"""
        super().validate()
        self._validate_youtube()
        self._validate_slideshare()
        self._validate_website()
        self._log_errors()
        return not self.errors

    def _get_url_content(self, url):
        """Performs a HTTP GET on the url.

        Returns False if the url is invalid or not-found"""
        rv = None
        if not re.search(r'^http', url):
            url = 'http://' + url
        try:
            req = urllib.request.urlopen(url, None, 10)
            rv = req.read().decode("utf-8")
            req.close()
        except urllib.request.URLError:
            return None
        except ValueError:
            return None
        return rv

    def _log_errors(self):
        """Put any form errors in logs as warning"""
        if self.errors:
            controller.app().logger.warn(self.errors)

    def _slideshare_code(self):
        """Download slideshare url and extract embed code.
        The original url may not have the code.
        ex. www.slideshare.net/Micahseff/game-xplain-pitch-deck-81610
        Adds field errors if the code can not be determined.
        """
        html = self._get_url_content(self.slideshow_url.data)
        if not html:
            self.slideshow_url.errors = ['Invalid SideShare URL.']
            return None
        m = re.search(r'slideshow/embed_code/(\d+)', html)
        if m:
            return m.group(1)
        self.slideshow_url.errors = ['Embed code not found on SlideShare page.']
        return None
        
    def _update_models(self, contest):
        """Creates the Contestant and Founder models
        and adds BivAccess models to join the contest and Founder models"""
        contestant = pcm.Contestant()
        self.populate_obj(contestant)
        contestant.youtube_code = self._youtube_code()
        contestant.slideshow_code = self._slideshare_code()
        contestant.is_public = controller.app().config[
            'PP_ALL_PUBLIC_CONTESTANTS']
        founder = pcm.Founder()
        self.populate_obj(founder)
        founder.display_name = flask.session['user.display_name']
        controller.db.session.add(contestant)
        controller.db.session.add(founder)
        controller.db.session.flush()
        controller.db.session.add(
            pam.BivAccess(
                source_biv_id=contest.biv_id,
                target_biv_id=contestant.biv_id
            )
        )
        controller.db.session.add(
            pam.BivAccess(
                source_biv_id=contestant.biv_id,
                target_biv_id=founder.biv_id
            )
        )
        controller.db.session.add(
            pam.BivAccess(
                source_biv_id=flask.session['user.biv_id'],
                target_biv_id=founder.biv_id
            )
        )
        return contestant

    def _youtube_code(self):
        """Ensure the youtube url contains a VIDEO_ID"""
        value = self.youtube_url.data
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

    def _validate_slideshare(self):
        """Ensures the SlideShare slide deck exists"""
        if self.slideshow_url.errors:
            return
        code = self._slideshare_code()
        if code:
            if not self._get_url_content(
                'http://www.slideshare.net/slideshow/embed_code/' + code):
                self.slideshow_url.errors = [
                    'Unknown SlideShare ID: ' + code + '.']

    def _validate_website(self):
        """Ensures the website exists"""
        if self.website.errors:
            return
        if self.website.data:
            if not self._get_url_content(self.website.data):
                self.website.errors = ['Website invalid or unavailable.']

    def _validate_youtube(self):
        """Ensures the YouTube video exists"""
        if self.youtube_url.errors:
            return
        code = self._youtube_code()
        if code:
            if not self._get_url_content('http://youtu.be/' + code):
                self.youtube_url.errors = [
                    'Unknown YouTube VIDEO_ID: ' + code + '.']
        else:
            self.youtube_url.errors = ['Invalid YouTube URL.']
