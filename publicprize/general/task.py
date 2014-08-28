# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import flask
from flask_oauthlib.client import OAuth, OAuthException
from publicprize import controller
import publicprize.auth.model as pam
import publicprize.contest.model as pcm
import werkzeug

facebook = OAuth(controller.app()).remote_app(
    'facebook',
    consumer_key=controller.app().config['FACEBOOK_APP_ID'],
    consumer_secret=controller.app().config['FACEBOOK_APP_SECRET'],
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
            contests=pcm.Contest.query.all()
        )

    def action_facebook_login(biv_obj):
        controller.app().logger.info(flask.request.referrer);
        callback = flask.url_for(
            '_route',
            path=biv_obj.format_uri('facebook_authorized'),
            # TODO(pjm): store next in session
            next=flask.request.args.get('next') or flask.request.referrer or None,
            _external=True
        )
        state = werkzeug.security.gen_salt(10)
        flask.session['oauth_state'] = state
        return facebook.authorize(
            callback=callback,
            state=state
        )

    def action_facebook_authorized(biv_obj):
        resp = facebook.authorized_response()
        app = controller.app()

        if resp is None:
            # TODO(pjm): flash message "facebook access denied"
            app.logger.info(
                'Access denied: reason=%s error=%s' % (
                    flask.request.args.get('error_reason'),
                    flask.request.args.get('error_description')
                )
            )
            return General.action_index(biv_obj)
        if isinstance(resp, OAuthException):
            # TODO(pjm): flash message "facebook access denied"
            app.logger.info('Access denied: %s' % resp.message)
            return General.action_index(biv_obj)
        if flask.session.get('oauth_state') != flask.request.args.get('state'):
            app.logger.info(
                'Invalid oauth state, expected: %s response: %s' % (
                    flask.session.get('oauth_state'),
                    flask.request.args.get('state')
                 )
            )
            return General.action_index(biv_obj)

#        flask.session['oauth_token'] = (resp['access_token'], '')
        app.logger.info(resp)
        token = (resp['access_token'], '')
        me = facebook.get(
            '/me',
            token=token
        )
        app.logger.info(me.data)
        app.logger.info(
            'Logged in as id=%s name=%s redirect=%s' % (
                me.data['id'], me.data['name'], flask.request.args.get('next'))
        )
        app.logger.info(flask.request.args);
        return flask.redirect(flask.request.args.get('next') or '/');
        
    def action_not_found(biv_obj):
        return flask.render_template('general/not-found.html'), 404

@facebook.tokengetter
def _get_facebook_oauth_token():
    return flask.session.get('oauth_token')
    
