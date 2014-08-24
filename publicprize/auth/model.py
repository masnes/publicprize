# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

from publicprize import db

# TODO(pjm): change biv_ids to Numeric(18) with sequence

class BivAccess(db.Model):
    source_biv_id = db.Column(db.Integer, primary_key=True)
    target_biv_id = db.Column(db.Integer, primary_key=True)

class User(db.Model):
    biv_id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(100))
    user_email = db.Column(db.String(100))

