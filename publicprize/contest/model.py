# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

from publicprize.controller import db
from publicprize import controller
from publicprize import biv

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
        # TODO(pjm): count related Contestant records
        return 12

    def donor_count(self):
        # TODO(pjm): count related Donor records
        return 802

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
Founder.BIV_MARKER = biv.register_marker(4, Founder)
