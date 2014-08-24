# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import json
from flask.ext.script import Manager, prompt_bool
from publicprize import app
from publicprize import db
import publicprize.auth.model
import publicprize.contest.model

manager = Manager(app)

@manager.command
def create_db():
    db.create_all();

@manager.command
def create_test_data():
    data = json.load(open('data/test_data.json', 'r'))

    for contest in data['Contest']:
        db.session.add(
            publicprize.contest.model.Contest(
                biv_id=contest['biv_id'],
                display_name=contest['display_name']
            )
        )

        for contestant in contest['Contestant']:
            db.session.add(
                publicprize.contest.model.Contestant(
                    biv_id=contestant['biv_id'],
                    display_name=contestant['display_name'],
                    youtube_code=contestant['youtube_code'],
                    slideshow_code=contestant['slideshow_code'],
                    contestant_desc=contestant['contestant_desc'],
                )
            )

            for founder in contestant['Founder']:
                db.session.add(
                    publicprize.contest.model.Founder(
                        biv_id=founder['biv_id'],
                        display_name=founder['display_name'],
                        founder_avatar=founder['founder_avatar'],
                        founder_desc=founder['founder_desc']
                    )
                )

    db.session.commit()

@manager.command
def create_test_db():
    drop_db();
    create_db();
    create_test_data();
    
@manager.command
def drop_db():
    if prompt_bool("Drop database?"):
        db.drop_all()

def _add_parent(parent, child):
    db.session.add(child)

if __name__ == "__main__":
    manager.run()
