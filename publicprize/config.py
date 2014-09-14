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
    PP_GOOGLE_APP_ID = os.environ.get('GOOGLE_APP_ID')
    PP_GOOGLE_APP_SECRET = os.environ.get('GOOGLE_APP_SECRET')
    import locale
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')

class DevConfig(BaseConfig):
    """Development config"""
    SECRET_KEY = 'ppsecret'
    DEBUG = True
    PP_DATABASE = 'pp'
    PP_DATABASE_USER = 'ppuser'
    PP_DATABASE_PASSWORD = 'pppass'
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@localhost/{}'.format(
        PP_DATABASE_USER, PP_DATABASE_PASSWORD, PP_DATABASE)
#    SQLALCHEMY_ECHO = True
    PP_ALL_PUBLIC_CONTESTANTS = True
    PP_TEST_USER = True


class ProdConfig(BaseConfig):
    """Production config"""
    pass
