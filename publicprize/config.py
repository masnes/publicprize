# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import os

class BaseConfig(object):
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    PP_FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
    PP_FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')

class DevConfig(BaseConfig):
    SECRET_KEY = "ppsecret"
    DEBUG = True
    PP_DATABASE = 'pp'
    PP_DATABASE_USER = 'ppuser'
    PP_DATABASE_PASSWORD = 'pppass'
    SQLALCHEMY_DATABASE_URI = 'postgresql://' + PP_DATABASE_USER + ':' + PP_DATABASE_PASSWORD + '@localhost/' + PP_DATABASE
#    SQLALCHEMY_ECHO = True
    PP_ALL_PUBLIC_CONTESTANTS = True

class ProdConfig(BaseConfig):
    pass
