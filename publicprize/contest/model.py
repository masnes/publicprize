# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

#from publicprize import db
#import angular_flask.core

#db = angular_flask.core.db

#import publicprize.app
#db = publicprize.app.db

#from publicprize.app import db

from publicprize.controller import db

# TODO(pjm): change biv_ids to Numeric(18) with sequence

class Contest(db.Model):
    BIV_TYPE = '001'
    biv_id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(100))

    def load_biv(biv_id):
        return None

class Contestant(db.Model):
    BIV_TYPE = '002'
    biv_id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(100))
    youtube_code = db.Column(db.String(500))
    slideshow_code = db.Column(db.String(500))
    contestant_desc = db.Column(db.String)
    tax_id = db.Column(db.Integer)

    def load_biv(biv_id):
        return None

class Founder(db.Model):
    BIV_TYPE = '003'
    biv_id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(100))
    founder_avatar = db.Column(db.String(500))
    founder_desc = db.Column(db.String)

    def load_biv(biv_id):
        return None
