# -*- coding: utf-8 -*-
""" pytest for :mod:publicprize.biv

    :copyright: Copyright (c) 2014 Bivio Software, Inc.  All Rights Reserved.
    :license: Apache, see LICENSE for more details.
"""

import pytest
from publicprize import biv
# Needed to initialize known biv.ids
import publicprize.general.task

def test_marker():
    assert biv.Marker(1) == 1
    assert biv.Marker(899) == 899
    for v in -1, 0, 900:
        with pytest.raises(AssertionError):
            biv.Marker(v)

def test_index():
    assert biv.Index(9) == 9
    assert biv.Index(1e15 - 1) == 1e15 - 1
    for v in 0, int(1e15):
        with pytest.raises(AssertionError):
            biv.Index(v)

def test_id():
    assert biv.Id(1001) == 1001
    i = biv.Id(3001)
    assert i.biv_marker == 1
    assert i.biv_index == 3
    assert i.to_biv_uri() == '_301'
    for v in (1000, 1):
        with pytest.raises(AssertionError):
            biv.Id(v)
