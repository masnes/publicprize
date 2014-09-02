# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

from publicprize.controller import db
from publicprize import controller
from publicprize import biv
import publicprize.auth.model as pam
import sqlalchemy.orm

class Contest(db.Model, controller.Model):
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
        return pam.BivAccess.query.select_from(Contestant).filter(
            pam.BivAccess.source_biv_id == self.biv_id,
            pam.BivAccess.target_biv_id == Contestant.biv_id,
            Contestant.is_public == True
        ).count()

    def donor_count(self):
        access_alias = sqlalchemy.orm.aliased(pam.BivAccess)
        return Donor.query.select_from(pam.BivAccess, access_alias).filter(
            pam.BivAccess.source_biv_id == self.biv_id,
            pam.BivAccess.target_biv_id == access_alias.source_biv_id,
            access_alias.target_biv_id == Donor.biv_id
        ).count()

    def user_has_submission(self):
        # TODO(pjm): check if current user is a founder for this contest
        return False

class Contestant(db.Model, controller.Model):
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

class Donor(db.Model, controller.Model):
    biv_id = db.Column(
        db.Numeric(18),
        db.Sequence('donor_s', start=1007, increment=1000),
        primary_key=True
    )
    
class Founder(db.Model, controller.Model):
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
