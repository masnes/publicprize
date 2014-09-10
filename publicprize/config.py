# -*- coding: utf-8 -*-
""" Flask configuration.

    :copyright: Copyright (c) 2014 Bivio Software, Inc.  All Rights Reserved.
    :license: Apache, see LICENSE for more details.
"""

import os

class BaseConfig(object):
    """Common config across dev/test/production"""
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    PP_FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
    PP_FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')

class DevConfig(BaseConfig):
    """Development config"""
    SECRET_KEY = "ppsecret"
    DEBUG = True
    PP_DATABASE = 'pp'
    PP_DATABASE_USER = 'ppuser'
    PP_DATABASE_PASSWORD = 'pppass'
    SQLALCHEMY_DATABASE_URI = 'postgresql://' + PP_DATABASE_USER + ':' + PP_DATABASE_PASSWORD + '@localhost/' + PP_DATABASE
#    SQLALCHEMY_ECHO = True
    PP_ALL_PUBLIC_CONTESTANTS = True
    PP_TEST_USER = True

class ProdConfig(BaseConfig):
    """Production config"""
    pass
