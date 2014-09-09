# -*- coding: utf-8 -*-
""" Database creation and test data loading

    :copyright: Copyright (c) 2014 Bivio Software, Inc.  All Rights Reserved.
    :license: Apache, see LICENSE for more details.
"""

import flask.ext.script as fes
import json
import os
import publicprize.controller as ppc
from publicprize.controller import db
import publicprize.auth.model
import publicprize.contest.model

# Needs to be explicit
ppc.init()
_manager = fes.Manager(ppc.app())

@_manager.command
def create_db():
    """Create the postgres user, database, and publicprize schema"""
    config = ppc.app().config
    os.system('createuser --user=postgres --no-superuser --no-createdb --no-createrole %s' % config['PP_DATABASE_USER'])
    os.system('echo "ALTER USER %s WITH PASSWORD \'%s\'; COMMIT;" | psql --user=postgres template1' % (config['PP_DATABASE_USER'], config['PP_DATABASE_PASSWORD']))
    os.system("createdb --encoding='utf8' --locale=en_US.UTF-8 --user=postgres --owner=%s %s" % (config['PP_DATABASE_USER'], config['PP_DATABASE']))
    db.create_all()

@_manager.command
def create_test_data():
    """Populate database with contents of data/test_data.json file"""
    data = json.load(open('data/test_data.json', 'r'))

    for contest in data['Contest']:
        contest_id = _add_model(_create_contest(contest))
        for contestant in contest['Contestant']:
            contestant_id = _add_model(publicprize.contest.model.Contestant(
                # TODO(pjm): there must be a way to do this in a map()
                display_name=contestant['display_name'],
                youtube_code=contestant['youtube_code'],
                slideshow_code=contestant['slideshow_code'],
                contestant_desc=contestant['contestant_desc'],
                is_public=True
            ))
            _add_owner(contest_id, contestant_id)

            for founder in contestant['Founder']:
                founder_id = _add_model(_create_founder(founder))
                _add_owner(contestant_id, founder_id)

            for donor in contestant['Donor']:
                donor_id = _add_model(publicprize.contest.model.Donor(
                    amount=donor['amount']
                ))
                _add_owner(contestant_id, donor_id)

    db.session.commit()

@_manager.command
def create_test_db():
    """Recreates the database and loads the test data from data/test_data.json"""
    drop_db()
    create_db()
    create_test_data()

@_manager.command
def drop_db():
    """Destroy the database"""
    if fes.prompt_bool("Drop database?"):
        # db.drop_all()
        os.system('dropdb --user=postgres %s' % ppc.app().config['PP_DATABASE'])

def _add_model(model):
    """Adds a SQLAlchemy model and returns it's biv_id"""
    db.session.add(model)
    # flush() makes biv_id available (executes the db sequence)
    db.session.flush()
    return model.biv_id
    
def _add_owner(parent_id, child_id):
    """Creates a BivAccess record between the parent and child ids"""
    db.session.add(
        publicprize.auth.model.BivAccess(
            source_biv_id=parent_id,
            target_biv_id=child_id
        )
    )

def _create_contest(contest):
    """Creates a SQLAlchemy model Contest with optional logo file"""
    model = publicprize.contest.model.Contest(
        display_name=contest['display_name'],
        tag_line=contest['tag_line']
    )
    if 'logo_filename' in contest:
        f = open(contest['logo_filename'], 'rb')
        model.contest_logo = f.read()
        model.logo_type = contest['logo_type']
        f.close()
    return model

# TODO(pjm): normalize up binary fields, combine with _create_contest()
def _create_founder(founder):
    """Creates a SQLAlchemy model Founder with optional avatar file"""
    model = publicprize.contest.model.Founder(
        display_name=founder['display_name'],
        founder_desc=founder['founder_desc']
    )
    if 'avatar_filename' in founder:
        f = open(founder['avatar_filename'], 'rb')
        model.founder_avatar = f.read()
        model.avatar_type = founder['avatar_type']
        f.close()
    return model
    
if __name__ == "__main__":
    _manager.run()
