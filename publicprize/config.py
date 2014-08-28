# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import os

class BaseConfig(object):
    SECRET_KEY = "ppsecret"
    FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')

class DevConfig(BaseConfig):
    DEBUG = True
    PP_DATABASE = 'pp'
    PP_DATABASE_USER = 'ppuser'
    PP_DATABASE_PASSWORD = 'pppass'
    SQLALCHEMY_DATABASE_URI = 'postgresql://' + PP_DATABASE_USER + ':' + PP_DATABASE_PASSWORD + '@localhost/' + PP_DATABASE
    SQLALCHEMY_ECHO = True

class ProdConfig(BaseConfig):
    # TODO(pjm): read from file
    SECRET_KEY = ""
    
