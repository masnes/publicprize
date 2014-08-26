# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import flask.ext.script as fes
import json
import publicprize.controller as ppc
from publicprize.controller import db
import publicprize.auth.model
import publicprize.contest.model

# Needs to be explicit
ppc.init()
_manager = fes.Manager(ppc.app())

@_manager.command
def create_db():
    db.create_all()

@_manager.command
def create_test_data():
    data = json.load(open('data/test_data.json', 'r'))

    for contest in data['Contest']:
        db.session.add(
            _create_contest(contest)
        )

        for contestant in contest['Contestant']:
            db.session.add(
                publicprize.contest.model.Contestant(
                    # TODO(pjm): there must be a way to do this in a map()
                    biv_id=contestant['biv_id'],
                    display_name=contestant['display_name'],
                    youtube_code=contestant['youtube_code'],
                    slideshow_code=contestant['slideshow_code'],
                    contestant_desc=contestant['contestant_desc'],
                )
            )
            _add_owner(contest, contestant)

            for founder in contestant['Founder']:
                db.session.add(
                    _create_founder(founder)
                )
                _add_owner(contest, founder)
                _add_owner(contestant, founder)

    db.session.commit()

@_manager.command
def create_test_db():
    drop_db()
    create_db()
    create_test_data()
    
@_manager.command
def drop_db():
    if fes.prompt_bool("Drop database?"):
        db.drop_all()

def _add_owner(parent, child):
    db.session.add(
        publicprize.auth.model.BivAccess(
            source_biv_id=parent['biv_id'],
            target_biv_id=child['biv_id']
        )
    )

def _create_contest(contest):
    model = publicprize.contest.model.Contest(
        biv_id=contest['biv_id'],
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
    model = publicprize.contest.model.Founder(
        biv_id=founder['biv_id'],
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
