# -*- coding: utf-8 -*-
""" Flask configuration.

    :copyright: Copyright (c) 2014 Bivio Software, Inc.  All Rights Reserved.
    :license: Apache, see LICENSE for more details.
"""

import os

class Config(object):
    """Configuration driven off environment variables"""
    import locale
    locale.setlocale(locale.LC_ALL, '')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    PUBLICPRIZE = {}
    for x in (
        ('FACEBOOK_APP_ID', '524730380959867'),
        ('FACEBOOK_APP_SECRET', '3c3b466006521f5a7749d359eac1b909'),
        ('GOOGLE_APP_ID', '52174292586-2m801c1cb6rrir017uskgak8uhrit7gq.apps.googleusercontent.com'),
        ('GOOGLE_APP_SECRET', '6GP79ee_YgrTScaGIqsIdlue'),
        ('PAYPAL_MODE', 'sandbox'),
        ('PAYPAL_CLIENT_ID', 'AX4PLRDhLD9Vfw-Nofq5cl9pJ00Db8m_gLoXWSPLcrsNLz3xFr1HBefnhZ9W'),
        ('PAYPAL_CLIENT_SECRET', 'EJQnKBBhBDdTw-3qVKN4oIjxyYmOMTYAb2U-xIfXapey45wryeGmzyX4OtpM')):
        if not x[0] in os.environ:
            os.environ[x[0]] = x[1]
        PUBLICPRIZE[x[0]] = os.environ.get(x[0])
    #TODO: get from environ
    SECRET_KEY = 'ppsecret'
    DEBUG = True
    PUBLICPRIZE['DATABASE'] = {
        'name': 'pp',
        'user': 'ppuser',
        'password': 'pppass',
        'host': 'localhost',
        'postgres_pass': 'postpass'}
    PUBLICPRIZE['ALL_PUBLIC_CONTESTANTS'] = True
    PUBLICPRIZE['TEST_USER'] = True
    SQLALCHEMY_DATABASE_URI = \
        'postgresql://{user}:{password}@{host}/{name}'.format(**PUBLICPRIZE['DATABASE'])
#    SQLALCHEMY_ECHO = True
