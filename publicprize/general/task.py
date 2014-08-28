# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import flask
from flask_oauthlib.client import OAuth, OAuthException
from publicprize import controller
from publicprize.auth.model import User
import publicprize.contest.model
import werkzeug

facebook = OAuth(controller.app()).remote_app(
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
    def action_index(biv_obj):
        return flask.render_template(
            "general/index.html",
            contests=publicprize.contest.model.Contest.query.all()
        )

    def action_facebook_login(biv_obj):
        callback = flask.url_for(
            '_route',
            path=biv_obj.format_uri('facebook_authorized'),
            _external=True
        )
        # return to the "next" or referrer page when return from callback
        controller.session()['oauth.next_uri'] = flask.request.args.get('next') or flask.request.referrer or None
        state = werkzeug.security.gen_salt(10)
        controller.session()['oauth.state'] = state
        return facebook.authorize(
            callback=callback,
            state=state
        )

    def action_facebook_authorized(biv_obj):
        resp = facebook.authorized_response()
        session = controller.session()
        next = None
        if 'oauth.next_uri' in session:
            next = session['oauth.next_uri']
            del session['oauth.next_uri']
        if not General._facebook_validate_auth(resp):
            return flask.redirect(next or '/')
        session['oauth.token'] = (resp['access_token'], '')
        General._facebook_user(
            facebook.get('/me', token=(resp['access_token'], '')).data
        )
        return flask.redirect(next or '/')

    def action_logout(biv_obj):
        session = controller.session()
        session['user.is_logged_in'] = False
        del session['oauth.token']
        # TODO(pjm): flash logged-out message
        return flask.redirect('/')
        
    def action_not_found(biv_obj):
        return flask.render_template('general/not-found.html'), 404

    def _facebook_user(info):
        # info contains email, last_name, first_name, id, name
        controller.app().logger.info(info)
        # avatar link
        # https://graph.facebook.com/{id}/picture?type=square
        user = User.query.filter_by(
            oauth_type='facebook',
            oauth_id=info['id']
        ).first()
        if user == None:
            user = User(
                display_name=info['name'],
                user_email=info['email'],
                oauth_type='facebook',
                oauth_id=info['id']
            )
        else:
            user.display_name = info['name']
            user.user_email = info['email']
        controller.db.session.add(user)
        controller.db.session.flush()
        session = controller.session()
        session['user.biv_id'] = user.biv_id
        session['user.is_logged_in'] = True
        session['user.display_name'] = user.display_name
        
    def _facebook_validate_auth(resp):
        app = controller.app()
        
        if resp is None:
            # TODO(pjm): flash message "facebook access denied"
            app.logger.warn(
                'Access denied: reason=%s error=%s' % (
                    flask.request.args.get('error_reason'),
                    flask.request.args.get('error_description')
                )
            )
            return False
        if isinstance(resp, OAuthException):
            # TODO(pjm): flash message "facebook access denied"
            app.logger.warn(resp)
            return False
        session = controller.session()
        state = session['oauth.state']
        del session['oauth.state']
        if state != flask.request.args.get('state'):
            # TODO(pjm): flash message "facebook access denied"
            app.logger.warn(
                'Invalid oauth state, expected: %s response: %s' % (
                    state,
                    flask.request.args.get('state')
                 )
            )
            return False
        return True

@facebook.tokengetter
def _get_facebook_oauth_token():
    return controller.session().get('oauth.token')
    
