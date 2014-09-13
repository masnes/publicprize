# -*- coding: utf-8 -*-
""" Enhanced functions based on :py:mod:`inspect`

    :copyright: (c) 2014 Bivio Software, Inc.
    :license: Apache, see LICENSE for more details.
"""

import inspect


def class_has_method(cls, method):
    """Does cls or its ancestors implement method?"""
    for name in inspect.getmro(cls):
        if hasattr(name, method) and inspect.ismethod(getattr(name, method)):
            return True
    return False
