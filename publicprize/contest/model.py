# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

from publicprize.controller import db
import publicprize.controller as ppc

# TODO(pjm): change biv_ids to Numeric(18) with sequence

class Contest(db.Model, ppc.Model):
    BIV_TYPE = '001'
    biv_id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(100), nullable=False)
    tag_line = db.Column(db.String(500))
    contest_logo = db.Column(db.LargeBinary)
    logo_type = db.Column(db.Enum('gif', 'png', 'jpeg'))

    def contestant_count(self):
        # TODO(pjm): count related Contestant records
        return 12

    def donor_count(self):
        # TODO(pjm): count related Donor records
        return 802

class Contestant(db.Model, ppc.Model):
    BIV_TYPE = '002'
    biv_id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(100), nullable=False)
    youtube_code = db.Column(db.String(500))
    slideshow_code = db.Column(db.String(500))
    contestant_desc = db.Column(db.String)
    tax_id = db.Column(db.Integer)

class Founder(db.Model, ppc.Model):
    BIV_TYPE = '003'
    biv_id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(100), nullable=False)
    founder_avatar = db.Column(db.String(500))
    founder_desc = db.Column(db.String)
