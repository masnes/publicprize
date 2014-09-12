# -*- coding: utf-8 -*-
""" Global tasks.

    :copyright: Copyright (c) 2014 Bivio Software, Inc.  All Rights Reserved.
    :license: Apache, see LICENSE for more details.
"""

import flask
from flask_oauthlib.client import OAuth, OAuthException
from publicprize import controller
from publicprize.auth.model import User
import publicprize.contest.model
import werkzeug

# TODO(pjm): move to auth.facebook
_FACEBOOK = OAuth(controller.app()).remote_app(
    'facebook',
    consumer_key=controller.app().config['PP_FACEBOOK_APP_ID'],
    consumer_secret=controller.app().config['PP_FACEBOOK_APP_SECRET'],
    request_token_params={'scope': 'email'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth'
)


class General(controller.Task):
    """Global tasks"""
    def action_index(biv_obj):
        """Site index"""
        return flask.render_template(
            "general/index.html",
            contests=publicprize.contest.model.Contest.query.all()
        )

    def action_facebook_login(biv_obj):
        """Login with facebook."""
        callback = biv_obj.format_absolute_uri('facebook-authorized')
        # return to the "next" or referrer page when return from callback
        flask.session['oauth.next_uri'] = flask.request.args.get('next') \
            or flask.request.referrer or None
        state = werkzeug.security.gen_salt(64)
        flask.session['oauth.state'] = state
        return _FACEBOOK.authorize(
            callback=callback,
            state=state
        )

    def action_facebook_authorized(biv_obj):
        """Facebook login response"""
        resp = _FACEBOOK.authorized_response()
        next_uri = None
        if 'oauth.next_uri' in flask.session:
            next_uri = flask.session['oauth.next_uri']
            del flask.session['oauth.next_uri']
        if not General._facebook_validate_auth(resp):
            return flask.redirect(next_uri or '/')
        flask.session['oauth.token'] = (resp['access_token'], '')
        General._facebook_user(
            _FACEBOOK.get('/me', token=(resp['access_token'], '')).data
        )
        return flask.redirect(next_uri or '/')

    def action_logout(biv_obj):
        """Logout"""
        flask.session['user.is_logged_in'] = False
        del flask.session['oauth.token']
        flask.flash('You have successfully logged out.')
        return flask.redirect('/')

    def action_not_found(biv_obj):
        """Not found page"""
        return flask.render_template('general/not-found.html'), 404

    def action_new_test_user(biv_obj):
        """Creates a new test user model and log in."""
        if not controller.app().config['PP_TEST_USER']:
            raise Error("PP_TEST_USER not enabled")
        flask.session['oauth.token'] = werkzeug.security.gen_salt(64)
        name = 'F{} L{}'.format(
            werkzeug.security.gen_salt(6).lower(),
            werkzeug.security.gen_salt(8).lower())
        user = User(
            display_name=name,
            user_email='{}@localhost'.format(name.lower()),
            oauth_type='test',
            oauth_id=werkzeug.security.gen_salt(64)
        )
        General._add_user_to_session(user)
        return flask.redirect('/')

    def _add_user_to_session(user):
        """Store user info on session"""
        controller.db.session.add(user)
        controller.db.session.flush()
        flask.session['user.biv_id'] = user.biv_id
        flask.session['user.is_logged_in'] = True
        flask.session['user.display_name'] = user.display_name

    def _facebook_user(info):
        """Saves facebook info to user model."""
        # info contains email, last_name, first_name, id, name
        controller.app().logger.info(info)
        if not info.get('email'):
            del flask.session['oauth.token']
            flask.flash('Your email must be provided to this App to login.')
            return
        # avatar link
        # https://graph.facebook.com/{id}/picture?type=square
        user = User.query.filter_by(
            oauth_type='facebook',
            oauth_id=info['id']
        ).first()
        if user:
            user.display_name = info['name']
            user.user_email = info['email']
        else:
            user = User(
                display_name=info['name'],
                user_email=info['email'],
                oauth_type='facebook',
                oauth_id=info['id']
            )
        General._add_user_to_session(user)

    def _facebook_validate_auth(resp):
        """Validates facebook's auth response"""
        app = controller.app()

        if resp is None:
            flask.flash('Facebook has denied access to this App.')
            app.logger.warn(
                'Access denied: reason={} error={}'.format(
                    flask.request.args.get('error_reason'),
                    flask.request.args.get('error_description'))
            )
            return False
        if isinstance(resp, OAuthException):
            flask.flash('Facebook has denied access to this App.')
            app.logger.warn(resp)
            return False
        state = flask.session['oauth.state']
        del flask.session['oauth.state']
        if state != flask.request.args.get('state'):
            flask.flash('Facebook has denied access to this App.')
            app.logger.warn(
                'Invalid oauth state, expected: {} response: {}'.format(
                    state,
                    flask.request.args.get('state'))
            )
            return False
        return True


@_FACEBOOK.tokengetter
def _get_facebook_oauth_token():
    """Callback for facebook auth"""
    return flask.session.get('oauth.token')
