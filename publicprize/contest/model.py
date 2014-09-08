# -*- coding: utf-8 -*-
""" contest models: Contest, Contestant, Donor, and Founder

    :copyright: Copyright (c) 2014 Bivio Software, Inc.  All Rights Reserved.
    :license: Apache, see LICENSE for more details.
"""

import flask
from publicprize.controller import db
from publicprize import controller
from publicprize import biv
import publicprize.auth.model as pam
import sqlalchemy.orm

class Contest(db.Model, controller.Model):
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
            Contestant.is_public == True
        ).count()

    def donor_count(self):
        """Returns the total donor count across all the contestants"""
        access_alias = sqlalchemy.orm.aliased(pam.BivAccess)
        return Donor.query.select_from(pam.BivAccess, access_alias).filter(
            pam.BivAccess.source_biv_id == self.biv_id,
            pam.BivAccess.target_biv_id == access_alias.source_biv_id,
            access_alias.target_biv_id == Donor.biv_id
        ).count()

    def user_submission_url(self):
        """Returns the current user's submission url or None.
        Iterates all the contest's contestant's founders, matching with
        the current logged in user.
        """
        access_alias = sqlalchemy.orm.aliased(pam.BivAccess)
        founders = Founder.query.select_from(pam.BivAccess, access_alias).filter(
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

class Contestant(db.Model, controller.Model):
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

class Donor(db.Model, controller.Model):
    """donor database model.

    Fields:
        biv_id: primary ID
    """
    biv_id = db.Column(
        db.Numeric(18),
        db.Sequence('donor_s', start=1007, increment=1000),
        primary_key=True
    )
    
class Founder(db.Model, controller.Model):
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
