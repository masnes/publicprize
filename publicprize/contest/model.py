# -*- coding: utf-8 -*-
""" contest models: Contest, Contestant, Donor, and Founder

    :copyright: Copyright (c) 2014 Bivio Software, Inc.  All Rights Reserved.
    :license: Apache, see LICENSE for more details.
"""

import decimal
import flask
import locale
from publicprize.controller import db
from publicprize import common
from publicprize import controller
from publicprize import biv
import publicprize.auth.model as pam
import sqlalchemy.orm


class Contest(db.Model, common.ModelWithDates):
    """contest database model.

    Fields:
        biv_id: primary ID
        display_name: name of the contest
        tag_line: sub-name of the contest
        contest_logo: image blob
        logo_type: image type (gif, png, jpeg)
    """
    biv_id = db.Column(
        db.Numeric(18),
        db.Sequence('contest_s', start=1002, increment=1000),
        primary_key=True
    )
    display_name = db.Column(db.String(100), nullable=False)
    tag_line = db.Column(db.String(500))
    # TODO(pjm): move logo and founder_avatar to separate model BivImage
    contest_logo = db.Column(db.LargeBinary)
    logo_type = db.Column(db.Enum('gif', 'png', 'jpeg', name='logo_type'))

    def contestant_count(self):
        """Returns the number of contestants for the current contest"""
        return pam.BivAccess.query.select_from(Contestant).filter(
            pam.BivAccess.source_biv_id == self.biv_id,
            pam.BivAccess.target_biv_id == Contestant.biv_id,
            # not a real ==, Column() overrides __eq__ to generate SQL
            Contestant.is_public == True  # noqa
        ).count()

    def donor_count(self):
        """Returns the total donor count across all the contestants"""
        access_alias = sqlalchemy.orm.aliased(pam.BivAccess)
        return Donor.query.select_from(pam.BivAccess, access_alias).filter(
            pam.BivAccess.source_biv_id == self.biv_id,
            pam.BivAccess.target_biv_id == access_alias.source_biv_id,
            access_alias.target_biv_id == Donor.biv_id,
            Donor.donor_state == 'executed'
        ).count()

    def donor_executed_amount(self):
        """Returns the total amount raised for all executed donors"""
        access_alias = sqlalchemy.orm.aliased(pam.BivAccess)
        # TODO(pjm): do sum in sql query
        rows = Donor.query.select_from(pam.BivAccess, access_alias).filter(
            pam.BivAccess.source_biv_id == self.biv_id,
            pam.BivAccess.target_biv_id == access_alias.source_biv_id,
            access_alias.target_biv_id == Donor.biv_id,
            Donor.donor_state == 'executed'
        ).all()
        total = decimal.Decimal(0)
        for row in rows:
            total += row.amount
        # TODO(pjm): use UI widget to do formatting
        return locale.format('%d', total, grouping=True)

    def user_submission_url(self):
        """Returns the current user's submission url or None.
        Iterates all the contest's contestant's founders, matching with
        the current logged in user.
        """
        access_alias = sqlalchemy.orm.aliased(pam.BivAccess)
        founders = Founder.query.select_from(
            pam.BivAccess, access_alias
        ).filter(
            pam.BivAccess.source_biv_id == self.biv_id,
            pam.BivAccess.target_biv_id == access_alias.source_biv_id,
            access_alias.target_biv_id == Founder.biv_id
        ).all()

        for founder in founders:
            if Founder.query.select_from(pam.BivAccess).filter(
                    pam.BivAccess.source_biv_id == flask.session['user.biv_id'],
                    pam.BivAccess.target_biv_id == founder.biv_id
            ).first():
                return Contestant.query.select_from(pam.BivAccess).filter(
                    pam.BivAccess.source_biv_id == Contestant.biv_id,
                    pam.BivAccess.target_biv_id == founder.biv_id
                ).one().format_uri('contestant')
        return None


class Contestant(db.Model, common.ModelWithDates):
    """contestant database model.

    Fields:
        biv_id: primary ID
        display_name: project name
        youtube_code: the VIDEO_ID for the youtube video
        slideshow_code: the SlideShare ID for the slide deck
        contestant_desc: project description
        tax_id: project EIN
        website: project website
        is_public: is the project to be shown on the public contestant list?
    """
    biv_id = db.Column(
        db.Numeric(18),
        db.Sequence('contestant_s', start=1003, increment=1000),
        primary_key=True
    )
    display_name = db.Column(db.String(100), nullable=False)
    youtube_code = db.Column(db.String(500))
    slideshow_code = db.Column(db.String(500))
    contestant_desc = db.Column(db.String)
    tax_id = db.Column(db.Numeric(9))
    website = db.Column(db.String(100))
    is_public = db.Column(db.Boolean, nullable=False)

    def get_contest(self):
        """Returns the Contest model which owns this Contestant"""
        return Contest.query.select_from(pam.BivAccess).filter(
            pam.BivAccess.source_biv_id == Contest.biv_id,
            pam.BivAccess.target_biv_id == self.biv_id
        ).one()

    def get_founders(self):
        """Return a list of Founder models for this Contestant"""
        return Founder.query.select_from(pam.BivAccess).filter(
            pam.BivAccess.source_biv_id == self.biv_id,
            pam.BivAccess.target_biv_id == Founder.biv_id
        ).all()


class Donor(db.Model, common.ModelWithDates):
    """donor database model.

    Fields:
        biv_id: primary ID
        amount: promised amount
        display_name: donor name, from paypal
        donor_email: donor email, from paypal
        donor_state: (submitted, pending_confirmation, executed, canceled)
        paypal_payment_id: payment id, from paypal post
        paypal_payer_id: payer id, from paypal url callback
    """
    biv_id = db.Column(
        db.Numeric(18),
        db.Sequence('donor_s', start=1007, increment=1000),
        primary_key=True
    )
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    display_name = db.Column(db.String(100))
    donor_email = db.Column(db.String(100))
    donor_state = db.Column(db.Enum(
        'submitted', 'pending_confirmation', 'executed', 'canceled',
        name='donor_state'))
    paypal_payment_id = db.Column(db.String(100))
    paypal_payer_id = db.Column(db.String(100))

    def add_to_session(self):
        """Add the donor to the session by biv_id."""
        controller.db.session.add(self)
        controller.db.session.flush()
        flask.session['donor.biv_id'] = self.biv_id

    def remove_from_session(self):
        """Remove the donor's biv_id from the session, if present."""
        if flask.session.get('donor.biv_id'):
            del flask.session['donor.biv_id']

    @staticmethod
    def unsafe_load_from_session():
        """Loads the donor from the session.
        Returns None if session value is missing or donor does not exist.
        """
        if flask.session.get('donor.biv_id'):
            return Donor.query.filter_by(
                biv_id=flask.session['donor.biv_id']
            ).first()
        return None


class Founder(db.Model, common.ModelWithDates):
    """founder database model.

    Fields:
        biv_id: primary ID
        display_name: donor full name
        fouder_desc: founder's short bio
        founder_avatar: avatar image blob
        avatar_type: image type (gif, png, jpeg)
    """
    biv_id = db.Column(
        db.Numeric(18),
        db.Sequence('founder_s', start=1004, increment=1000),
        primary_key=True
    )
    display_name = db.Column(db.String(100), nullable=False)
    founder_desc = db.Column(db.String)
    founder_avatar = db.Column(db.LargeBinary)
    avatar_type = db.Column(db.Enum('gif', 'png', 'jpeg', name='avatar_type'))

Contest.BIV_MARKER = biv.register_marker(2, Contest)
Contestant.BIV_MARKER = biv.register_marker(3, Contestant)
Donor.BIV_MARKER = biv.register_marker(7, Donor)
Founder.BIV_MARKER = biv.register_marker(4, Founder)
