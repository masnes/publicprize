# -*- coding: utf-8 -*-
""" Flask configuration.

    :copyright: Copyright (c) 2014 Bivio Software, Inc.  All Rights Reserved.
    :license: Apache, see LICENSE for more details.
"""

import os


class BaseConfig(object):
    """Common config across dev/test/production"""
    import locale
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

class DevConfig(BaseConfig):
    """Development config"""
    PP_FACEBOOK_APP_ID = os.environ.get(
        'FACEBOOK_APP_ID', '524730380959867')
    PP_FACEBOOK_APP_SECRET = os.environ.get(
        'FACEBOOK_APP_SECRET', '3c3b466006521f5a7749d359eac1b909')
    PP_GOOGLE_APP_ID = os.environ.get(
        'GOOGLE_APP_ID',
        '52174292586-2m801c1cb6rrir017uskgak8uhrit7gq.apps.googleusercontent.com')
    PP_GOOGLE_APP_SECRET = os.environ.get(
        'GOOGLE_APP_SECRET', '6GP79ee_YgrTScaGIqsIdlue')
    for x in (
        ('PAYPAL_MODE', 'sandbox'),
        ('PAYPAL_CLIENT_ID', 'AX4PLRDhLD9Vfw-Nofq5cl9pJ00Db8m_gLoXWSPLcrsNLz3xFr1HBefnhZ9W'),
        ('PAYPAL_CLIENT_SECRET', 'EJQnKBBhBDdTw-3qVKN4oIjxyYmOMTYAb2U-xIfXapey45wryeGmzyX4OtpM')):
        if not x[0] in os.environ:
            os.environ[x[0]] = x[1]
    SECRET_KEY = 'ppsecret'
    DEBUG = True
    PP_DATABASE = {
        'name': 'pp',
        'user': 'ppuser',
        'password': 'pppass',
        'host': 'localhost',
        'postgres_pass': 'postpass'}
    SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{password}@{host}/{name}'.format(**PP_DATABASE)
#    SQLALCHEMY_ECHO = True
    PP_ALL_PUBLIC_CONTESTANTS = True
    PP_TEST_USER = True


class ProdConfig(BaseConfig):
    """Production config"""
    pass
