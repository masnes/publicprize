# -*- coding: utf-8 -*-
""" OAuth support, facebook and google.

Session variables:

user.biv_id: User's id, survives after log out
user.oauth_type, User's oauth_type, cleared during log out
user.is_logged_in, User's logged in status
user.display_name, User's full name

oauth.next_uri, redirect uri after successful login,
    cleared after authorize_complete()
oauth.state, oauth state var, cleared after authorize_complete()
oauth.<oauth_type>.token, user's oauth token, cleared during log out

    :copyright: Copyright (c) 2014 Bivio Software, Inc.  All Rights Reserved.
    :license: Apache, see LICENSE for more details.
"""

import flask
import flask_oauthlib.client
from publicprize import controller
from publicprize.auth.model import User
import werkzeug


def _oauth_provider(name, **kwargs):
    """Creates a OAuth client for the named provider."""
    config = controller.app().config
    return flask_oauthlib.client.OAuth(controller.app()).remote_app(
        name,
        consumer_key=config['PP_{}_APP_ID'.format(name.upper())],
        consumer_secret=config['PP_{}_APP_SECRET'.format(name.upper())],
        request_token_url=None,
        **kwargs
    )

_OAUTH_PROVIDER = {
    'facebook': _oauth_provider(
        'facebook',
        request_token_params={'scope': 'email'},
        base_url='https://graph.facebook.com',
        access_token_url='/oauth/access_token',
        authorize_url='https://www.facebook.com/dialog/oauth'
    ),
    'google': _oauth_provider(
        'google',
        request_token_params={
            'scope': 'https://www.googleapis.com/auth/userinfo.email'
        },
        base_url='https://www.googleapis.com/oauth2/v1/',
        access_token_method='POST',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
    )
}

_OAUTH_PROVIDER_DATA_PATH = {
    'facebook': 'me',
    'google': 'userinfo',
}


def add_user_to_session(user):
    """Store user info on session"""
    controller.db.session.add(user)
    controller.db.session.flush()
    flask.session['user.biv_id'] = user.biv_id
    flask.session['user.oauth_type'] = user.oauth_type
    flask.session['user.is_logged_in'] = True
    flask.session['user.display_name'] = user.display_name


def authorize(oauth_type, callback):
    """Call the OAuth provider's server which returns to the callback
    on completion or failer.
    Store the "next" or referrer page to return to after callback."""
    flask.session['oauth.next_uri'] = flask.request.args.get('next') \
        or flask.request.referrer or None
    # state variable is uri randomizer, verfied in authorize_complete()
    state = werkzeug.security.gen_salt(64)
    flask.session['oauth.state'] = state
    return _OAUTH_PROVIDER[oauth_type].authorize(
        callback=callback,
        state=state
    )


def authorize_complete(oauth_type):
    """Handle oauth callback, validate the response and update the user
    model."""
    resp = _OAUTH_PROVIDER[oauth_type].authorized_response()
    next_uri = None
    if 'oauth.next_uri' in flask.session:
        next_uri = flask.session['oauth.next_uri']
        del flask.session['oauth.next_uri']
    if _validate_auth(resp, oauth_type):
        flask.session['oauth.{}.token'.format(oauth_type)] = (
            resp['access_token'], '')
        _user_from_info(
            oauth_type,
            _OAUTH_PROVIDER[oauth_type].get(
                _OAUTH_PROVIDER_DATA_PATH[oauth_type]).data
        )
    return flask.redirect(next_uri or '/')


def logout():
    """Clear the login state from the session and redirect to root."""
    _clear_session()
    flask.flash('You have successfully logged out.')
    return flask.redirect('/')


def _clear_session():
    """Clear the login state from the session"""
    flask.session['user.is_logged_in'] = False
    if 'oauth.state' in flask.session:
        del flask.session['oauth.state']
    oauth_type = flask.session.get('user.oauth_type')
    if oauth_type:
        key = 'oauth.{}.token'.format(oauth_type)
        if flask.session.get(key):
            del flask.session[key]
        del flask.session['user.oauth_type']


def _client_error(oauth_type, message=None):
    _clear_session()
    flask.flash(message \
        or '{} has denied access to this App.'.format(oauth_type))
        

def _user_from_info(oauth_type, info):
    """Saves oauth provider user info to user model.
    info arg contains email, id, name."""
    controller.app().logger.info(info)
    if not info.get('email'):
        _client_error(
            oauth, 'Your email must be provided to this App to login.')
        return
    user = User.query.filter_by(
        oauth_type=oauth_type,
        oauth_id=info['id']
    ).first()
    if user:
        user.display_name = info['name']
        user.user_email = info['email']
    else:
        user = User(
            display_name=info['name'],
            user_email=info['email'],
            oauth_type=oauth_type,
            oauth_id=info['id']
        )
    # TODO(pjm): download user avatar
    # facebook: https://graph.facebook.com/{id}/picture?type=square
    # google: image url provided in info.picture field
    add_user_to_session(user)


def _validate_auth(resp, oauth_type):
    """Validates oauth providers's auth response"""
    app = controller.app()

    if resp is None or isinstance(resp, flask_oauthlib.client.OAuthException):
        _client_error(oauth_type)
        app.logger.warn(
            'Access denied: {}, resp: {}'.format(flask.request.args, resp))
        return False
    state = flask.session['oauth.state']
    del flask.session['oauth.state']
    if state != flask.request.args.get('state'):
        _client_error(oauth_type)
        app.logger.warn(
            'Invalid oauth state, expected: {} response: {}'.format(
                state,
                flask.request.args.get('state'))
        )
        return False
    return True


_FACEBOOK = _OAUTH_PROVIDER['facebook']
_GOOGLE = _OAUTH_PROVIDER['google']


@_FACEBOOK.tokengetter
def _get_facebook_oauth_token():
    """Callback for facebook auth"""
    return flask.session.get('oauth.facebook.token')


@_GOOGLE.tokengetter
def _get_google_access_token():
    """Callback for google auth"""
    return flask.session.get('oauth.google.token')
