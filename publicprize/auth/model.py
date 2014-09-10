# -*- coding: utf-8 -*-
""" Auth models: BivAccess and User

    :copyright: Copyright (c) 2014 Bivio Software, Inc.  All Rights Reserved.
    :license: Apache, see LICENSE for more details.
"""

from publicprize import biv
from publicprize import controller
from publicprize.controller import db
from sqlalchemy import UniqueConstraint

class BivAccess(db.Model, controller.Model):
    """BivAccess links ownership between models. For example, a Contest model
    owns the Contestants and a User also owns their own Contestant submission.
    Fields:
        source_biv_id: the parent (owner) model
        target_biv_id: the child model
    """
    source_biv_id = db.Column(db.Numeric(18), primary_key=True)
    target_biv_id = db.Column(db.Numeric(18), primary_key=True)

class User(db.Model, controller.Model):
    """Logged-in User model.
    Fields:
        biv_id: primary ID
        display_name: user's full name
        user_email: user's email addrses
        oauth_type: the oauth server used to authenticate
        oauth_id: the user ID on the oauth server
    """
    # don't conflict with postgres "user" table
    __tablename__ = 'user_t'
    biv_id = db.Column(
        db.Numeric(18),
        db.Sequence('user_s', start=1006, increment=1000),
        primary_key=True
    )
    display_name = db.Column(db.String(100), nullable=False)
    # TODO(pjm): want unique constraint on email, will need to handle
    # error cases for multiple oauth_type attempts
    user_email = db.Column(db.String(100), nullable=False)
    oauth_type = db.Column(
        db.Enum('facebook', 'linkedin', 'google', 'test', name='oauth_type'),
        nullable=False
    )
    oauth_id = db.Column(db.String(100), nullable=False)
    __table_args__ = (UniqueConstraint('oauth_type', 'oauth_id'),)

BivAccess.BIV_MARKER = biv.register_marker(5, BivAccess)
User.BIV_MARKER = biv.register_marker(6, User)
