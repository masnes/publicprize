# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

from publicprize import biv
from publicprize import controller
from publicprize.controller import db

class BivAccess(db.Model, controller.Model):
    source_biv_id = db.Column(db.Numeric(18), primary_key=True)
    target_biv_id = db.Column(db.Numeric(18), primary_key=True)

class Session(db.Model, controller.Model):
    biv_id = db.Column(
        db.Numeric(18),
        db.Sequence('session_s', start=1007, increment=1000),
        primary_key=True
    )
    user_id = db.Column(db.Numeric(18))
    oauth_state = db.Column(db.String(10))
    oauth_next_url = db.Column(db.String(500))
    # oauth_type = db.Column(db.Enum('facebook', 'linkedin', 'google'))
    # user_state = db.Column(db.Enum('logged_in', 'logged_out'))

    # def is_logged_in(self):
    #     return self.user_state == 'logged_in'

    # def get_current_or_new():
    #     pass

class User(db.Model, controller.Model):
    biv_id = db.Column(
        db.Numeric(18),
        db.Sequence('user_s', start=1006, increment=1000),
        primary_key=True
    )
    display_name = db.Column(db.String(100))
    user_email = db.Column(db.String(100))

BivAccess.BIV_MARKER = biv.register_marker(5, BivAccess)
Session.BIV_MARKER = biv.register_marker(7, Session)
User.BIV_MARKER = biv.register_marker(6, User)
