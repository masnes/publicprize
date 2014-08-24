# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import flask.ext.script as fes
import json
import publicprize as pp
import publicprize.auth.model
import publicprize.contest.model

_manager = fes.Manager(pp.app)

@_manager.command
def create_db():
    pp.db.create_all();

@_manager.command
def create_test_data():
    data = json.load(open('data/test_data.json', 'r'))

    for contest in data['Contest']:
        pp.db.session.add(
            publicprize.contest.model.Contest(
                biv_id=contest['biv_id'],
                display_name=contest['display_name']
            )
        )

        for contestant in contest['Contestant']:
            pp.db.session.add(
                publicprize.contest.model.Contestant(
                    biv_id=contestant['biv_id'],
                    display_name=contestant['display_name'],
                    youtube_code=contestant['youtube_code'],
                    slideshow_code=contestant['slideshow_code'],
                    contestant_desc=contestant['contestant_desc'],
                )
            )
            _add_owner(contest, contestant);

            for founder in contestant['Founder']:
                pp.db.session.add(
                    publicprize.contest.model.Founder(
                        biv_id=founder['biv_id'],
                        display_name=founder['display_name'],
                        founder_avatar=founder['founder_avatar'],
                        founder_desc=founder['founder_desc']
                    )
                )
                _add_owner(contest, founder);
                _add_owner(contestant, founder);

    pp.db.session.commit()

@_manager.command
def create_test_db():
    drop_db();
    create_db();
    create_test_data();
    
@_manager.command
def drop_db():
    if fes.prompt_bool("Drop database?"):
        pp.db.drop_all()

def _add_owner(parent, child):
    pp.db.session.add(
        publicprize.auth.model.BivAccess(
            source_biv_id=parent['biv_id'],
            target_biv_id=child['biv_id']
        )
    )

if __name__ == "__main__":
    _manager.run()
