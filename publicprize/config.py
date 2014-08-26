# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import os

class BaseConfig(object):
    SECRET_KEY = "ppsecret"
    FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')

class DevConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/pp.db'
    SQLALCHEMY_ECHO = True

class ProdConfig(BaseConfig):
    # TODO(pjm): read from file
    SECRET_KEY = ""
    
