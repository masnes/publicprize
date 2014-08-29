# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

class ContestantForm(Form):
    display_name = StringField('Project Name', validators=[DataRequired()])
    contestant_desc = TextAreaField('Project Summary', validators=[DataRequired()])
    youtube_code = StringField(
        'YouTube Video Code',
        validators=[DataRequired()]
    )
    slideshow_code = StringField(
        'SlideShare Pitch Deck Code',
        validators=[DataRequired()]
    )
    founder_desc = StringField('Founder Short Bio', validators=[DataRequired()])
    website = StringField('Project Website')
