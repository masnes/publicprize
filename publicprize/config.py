# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

class BaseConfig(object):
    SECRET_KEY = "ppsecret"

class DevConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/pp.db'
    SQLALCHEMY_ECHO = True

class ProdConfig(BaseConfig):
    # TODO(pjm): read from file
    SECRET_KEY = ""
    
