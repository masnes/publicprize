# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

from flask.ext.script import Manager

from publicprize import app
from publicprize import db
import publicprize.auth.model
import publicprize.contest.model

manager = Manager(app)

@manager.command
def create_db():
    db.create_all();

@manager.command
def drop_db():
    db.drop_all()

if __name__ == "__main__":
    manager.run()
