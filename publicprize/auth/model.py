# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

from publicprize import biv
from publicprize import controller
from publicprize.controller import db

# TODO(pjm): change biv_ids to Numeric(18) with sequence

class BivAccess(db.Model, controller.Model):
    source_biv_id = db.Column(db.Integer, primary_key=True)
    target_biv_id = db.Column(db.Integer, primary_key=True)

class User(db.Model, controller.Model):
    biv_id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(100))
    user_email = db.Column(db.String(100))

BivAccess.BIV_MARKER = biv.register_marker(5, BivAccess)
User.BIV_MARKER = biv.register_marker(6, User)
