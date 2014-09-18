# -*- coding: utf-8 -*-
""" contest forms: HTTP form processing for contest pages

    :copyright: Copyright (c) 2014 Bivio Software, Inc.  All Rights Reserved.
    :license: Apache, see LICENSE for more details.
"""

import decimal
import flask
import flask_wtf
import locale
import paypalrestsdk
import paypalrestsdk.exceptions
import publicprize.auth.model as pam
import publicprize.contest.model as ppcm
import publicprize.controller as ppc
import re
import socket
import sys
import urllib.request
import wtforms
import wtforms.validators as wtfv

class Contestant(flask_wtf.Form):
    """Project submission form.

    Fields:
        display_name: project name
        contestant_desc: project summary
        youtube_url: full YouTube video url
        slideshow_url: full SlideShare url
        founder_desc: current user's founder info for this project
        website: project website (optional)
    """
    display_name = wtforms.StringField(
        'Legal Name of Business', validators=[wtfv.DataRequired()])
    contestant_desc = wtforms.TextAreaField(
        'Summary of Business, Product and/or Service',
        validators=[wtfv.DataRequired()])
    youtube_url = wtforms.StringField(
        'YouTube Video URL', validators=[wtfv.DataRequired()])
    slideshow_url = wtforms.StringField(
        'SlideShare Pitch Deck URL', validators=[wtfv.DataRequired()])
    founder_desc = wtforms.TextAreaField(
        'Your Short Bio', validators=[wtfv.DataRequired()])
    website = wtforms.StringField('Business Website')
    tax_id = wtforms.StringField(
        'Business US Tax Id', validators=[wtfv.DataRequired()])
    business_phone = wtforms.StringField(
        'Business Phone', validators=[wtfv.DataRequired()])
    business_address = wtforms.TextAreaField(
        'Business Mailing Address', validators=[wtfv.DataRequired()])

    def execute(self, contest):
        """Validates and creates the contestant model"""
        if self.is_submitted() and self.validate():
            contestant = self._update_models(contest)
            if contestant:
                flask.flash(
                    'Thank you for submitting your entry. You will be '
                    'contacted by email when your entry has been reviewed.')
                return flask.redirect(contestant.format_uri('contestant'))
        return flask.render_template(
            'contest/submit.html',
            contest=contest,
            form=self,
            selected='submit-contestant'
        )

    def validate(self):
        """Performs superclass wtforms validation followed by url
        field validation"""
        super().validate()
        self._validate_youtube()
        self._validate_slideshare()
        self._validate_website()
        _log_errors(self)
        return not self.errors

    def _get_url_content(self, url):
        """Performs a HTTP GET on the url.

        Returns False if the url is invalid or not-found"""
        res = None
        if not re.search(r'^http', url):
            url = 'http://' + url
        try:
            req = urllib.request.urlopen(url, None, 30)
            res = req.read().decode(locale.getlocale()[1])
            req.close()
        except urllib.request.URLError:
            return None
        except ValueError:
            return None
        except socket.timeout:
            return None
        return res

    def _slideshare_code(self):
        """Download slideshare url and extract embed code.
        The original url may not have the code.
        ex. www.slideshare.net/Micahseff/game-xplain-pitch-deck-81610
        Adds field errors if the code can not be determined.
        """
        html = self._get_url_content(self.slideshow_url.data)
        if not html:
            self.slideshow_url.errors = [
                'SlideShare URL invalid or unavailable.']
            return None
        match = re.search(r'slideshow/embed_code/(\d+)', html)
        if match:
            return match.group(1)
        self.slideshow_url.errors = [
            'Embed code not found on SlideShare page.']
        return None

    def _update_models(self, contest):
        """Creates the Contestant and Founder models
        and adds BivAccess models to join the contest and Founder models"""
        contestant = ppcm.Contestant()
        self.populate_obj(contestant)
        contestant.youtube_code = self._youtube_code()
        contestant.slideshow_code = self._slideshare_code()
        contestant.is_public = ppc.app().config['PUBLICPRIZE']['ALL_PUBLIC_CONTESTANTS']
        founder = ppcm.Founder()
        self.populate_obj(founder)
        founder.display_name = flask.session['user.display_name']
        ppc.db.session.add(contestant)
        ppc.db.session.add(founder)
        ppc.db.session.flush()
        ppc.db.session.add(
            pam.BivAccess(
                source_biv_id=contest.biv_id,
                target_biv_id=contestant.biv_id
            )
        )
        ppc.db.session.add(
            pam.BivAccess(
                source_biv_id=contestant.biv_id,
                target_biv_id=founder.biv_id
            )
        )
        ppc.db.session.add(
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
        if re.search(r'\?', value) and re.search(r'v\=', value):
            match = re.search(r'(?:\?|\&)v\=(.*)', value)
            if match:
                return match.group(1)
        else:
            match = re.search(r'\/([^\&\?\/]+)$', value)
            if match:
                return match.group(1)
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


class Donate(flask_wtf.Form):
    """Donation form.

    Fields:
        amount: donation amount
    """
    # TODO(pjm): DecimalField doesn't accept '' value...
    amount = wtforms.StringField('Contribution Amount')
    donate10 = wtforms.SubmitField('$10')
    donate25 = wtforms.SubmitField('$25')
    donate100 = wtforms.SubmitField('$100')
    other_amount = wtforms.SubmitField('Other Amount')

    def execute(self, contestant):
        """Validates and redirects to PayPal
        For test credit card payments, use card number: 4736656842918643
        """
        if self.is_submitted() and self.validate():
            url = self._paypal_payment(contestant)
            if url:
                return flask.redirect(url)
        return flask.render_template(
            'contest/detail.html',
            contestant=contestant,
            contest=contestant.get_contest(),
            form=self,
            founders=contestant.get_founders()
        )

    def execute_payment(self, contestant):
        """Handles return task from paypal. Calls paypal with payment and
        payer IDs to complete the transaction."""
        donor = ppcm.Donor.unsafe_load_from_session()
        if not donor:
            ppc.app().logger.warn('missing session donor')
            flask.flash('The referenced contribution was already processed.')
            return flask.redirect(contestant.format_uri())
        self._save_payment_info_to_donor(donor)
        payment = paypalrestsdk.Payment({
            'id': donor.paypal_payment_id
        })
        donor.remove_from_session()
        try:
            if payment.execute({'payer_id': donor.paypal_payer_id}):
                donor.donor_state = 'executed'
                ppc.db.session.add(donor)
                return flask.redirect(contestant.format_uri('thank-you'))
            else:
                ppc.app().logger.warn('payment execute failed')
        except paypalrestsdk.exceptions.ClientError as err:
            ppc.app().logger.warn(err)
        except:
            ppc.app().logger.warn(sys.exc_info()[0])
        return flask.redirect(contestant.format_uri())

    def validate(self):
        """Ensure the amount is present and at least $10"""
        super().validate()
        amount = None

        if self.donate10.data:
            amount = 10
        elif self.donate25.data:
            amount = 25
        elif self.donate100.data:
            amount = 100
        elif self.amount.data:
            try:
              if float(self.amount.data) < 10:
                  self.amount.errors = ['Amount must be at least $10.']
            except ValueError:
                self.amount.errors = ['Please enter an amount.']
        else:
            self.amount.errors = ['Please enter an amount.']
            self.amount.raw_data = None
        if amount:
            self.amount.data = decimal.Decimal(amount)
        _log_errors(self)
        return not self.errors

    def _create_donor(self, contestant):
        """Create a new donor model and link to the parent contestant."""
        donor = ppcm.Donor()
        self.populate_obj(donor)
        donor.donor_state = 'submitted'
        ppc.db.session.add(donor)
        ppc.db.session.flush()
        ppc.db.session.add(
            pam.BivAccess(
                source_biv_id=contestant.biv_id,
                target_biv_id=donor.biv_id
            )
        )
        return donor

    def _link_donor_to_user(self, donor):
        """Link the donor model to a user model. Match the donor email with
        the user. If no match, use the current user, if present."""
        if pam.BivAccess.query.select_from(pam.User).filter(
                pam.BivAccess.source_biv_id == pam.User.biv_id,
                pam.BivAccess.target_biv_id == donor.biv_id
        ).count() > 0:
            return
        user = pam.User.query.filter_by(user_email=donor.donor_email).first()
        if not user and flask.session.get('user.is_logged_in'):
            user = pam.User.query.filter_by(
                biv_id=flask.session['user.biv_id']
            ).one()
        if not user:
            return
        ppc.db.session.add(
            pam.BivAccess(
                source_biv_id=user.biv_id,
                target_biv_id=donor.biv_id
            )
        )

    def _paypal_payment(self, contestant):
        """Call paypal server to create payment record.
        Returns a redirect link to paypal site or None on error."""
        donor = self._create_donor(contestant)
        amount = '%.2f' % float(self.amount.data)
        payment = paypalrestsdk.Payment({
            'intent': 'sale',
            'payer': {
                'payment_method': 'paypal'
            },
            'redirect_urls': {
                'return_url': contestant.format_absolute_uri('donate-done'),
                'cancel_url': contestant.format_absolute_uri('donate-cancel'),
            },
            'transactions': [
                {
                    'amount': {
                        'total': amount,
                        'currency': 'USD',
                    },
                    'item_list': {
                        'items': [
                            {
                                'quantity': 1,
                                'price': amount,
                                'currency': 'USD',
                                'name': '{} contribution, {}'.format(
                                    contestant.display_name,
                                    contestant.get_contest().display_name),
                                'tax': 0
                            }
                        ]
                    }
                }
            ]
        })

        try:
            if payment.create():
                ppc.app().logger.info(payment)
                donor.paypal_payment_id = str(payment.id)
                donor.add_to_session()

                for link in payment.links:
                    if link.method == 'REDIRECT':
                        return str(link.href)
            else:
                ppc.app().logger.warn(payment.error)
        except paypalrestsdk.exceptions.ClientError as err:
            ppc.app().logger.warn(err)
        except:
            ppc.app().logger.warn(sys.exc_info()[0])
        self.amount.errors = [
            'There was an error processing your contribution.']
        return None

    def _save_payment_info_to_donor(self, donor):
        """Get payer info from paypal server, save info to Donor model."""
        try:
            payment = paypalrestsdk.Payment.find(donor.paypal_payment_id)
            info = payment.payer.payer_info
            donor.donor_email = info.email
            donor.display_name = info.first_name + ' ' + info.last_name
        except paypalrestsdk.exceptions.ConnectionError as err:
            ppc.app().logger.warn(err)
        donor.paypal_payer_id = flask.request.args['PayerID']
        donor.donor_state = 'pending_confirmation'
        ppc.db.session.add(donor)
        self._link_donor_to_user(donor)


def _log_errors(form):
    """Put any form errors in logs as warning"""
    if form.errors:
        ppc.app().logger.warn({
            'data': flask.request.form,
            'errors': form.errors
        })
