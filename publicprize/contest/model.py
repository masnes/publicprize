# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

# TODO(pjm): change biv_ids to Numeric(18) with sequence

class Contest(db.Model):
    biv_id = db.Column(db.Integer, primary_key = True)
    display_name = db.Column(db.String(100))

class Contestant(db.Model):
    biv_id = db.Column(db.Integer, primary_key = True)
    display_name = db.Column(db.String(100))
    youtube_code = db.Column(db.String(500))
    slideshow_code = db.Column(db.String(500))
    contestant_desc = db.Column(db.String)
    tax_id = db.Column(db.Integer)

class Founder(db.Model):
    biv_id = db.Column(db.Integer, primary_key = True)
    display_name = db.Column(db.String(100))
    founder_avatar = db.Column(db.String(500))
    founder_desc = db.Column(db.String)

    
