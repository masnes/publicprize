# -*- coding: utf-8 -*-
""" Database schema and data updates.

    :copyright: Copyright (c) 2014 Bivio Software, Inc.  All Rights Reserved.
    :license: Apache, see LICENSE for more details.
"""

import flask_script as fes
import manage
from publicprize.controller import db
import publicprize.contest.model as pcm
import publicprize.controller as ppc

# Needs to be explicit
ppc.init()
_MANAGER = fes.Manager(ppc.app())

@_MANAGER.option('-c', '--contest', help='Contest biv_id')
@_MANAGER.option('-s', '--name', help='Sponsor name')
@_MANAGER.option('-w', '--website', help='Sponsor website')
@_MANAGER.option('-i', '--input_file', help='Image file name')
def add_sponsor(contest, name, website, input_file):
    """Add the sponsor to the contest"""
    if not contest:
        raise Exception('missing contest')
    if not name:
        raise Exception('missing name')
    if not website:
        raise Exception('missing website')
    if not input_file:
        raise Exception('missing input_file')
    model = pcm.Contest().query.filter_by(biv_id=contest).one()
    manage.add_sponsor(model.biv_id, name, website, input_file)


if __name__ == '__main__':
    _MANAGER.run()
    
