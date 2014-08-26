# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

from publicprize import controller
import flask
from flask_oauthlib.client import OAuth, OAuthException

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
        return flask.render_template("general/index.html")

    def action_facebook_login(biv_obj):
        callback = flask.url_for(
            '_route',
            path=biv_obj.format_uri('facebook_authorized'),
            next=flask.request.args.get('next') or flask.request.referrer or None,
            _external=True
        )
        return facebook.authorize(callback=callback)

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

        flask.session['oauth_token'] = (resp['access_token'], '')
        me = facebook.get('/me')
        app.logger.info(me.data)
        app.logger.info(
            'Logged in as id=%s name=%s redirect=%s' % (
                me.data['id'], me.data['name'], flask.request.args.get('next'))
        )
        return flask.redirect(flask.request.args.get('next') or '/');
        
    def action_not_found(biv_obj):
        return flask.render_template('general/not-found.html'), 404

@facebook.tokengetter
def _get_facebook_oauth_token():
    return flask.session.get('oauth_token')
    
