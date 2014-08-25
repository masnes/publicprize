# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import flask
import flask.ext.sqlalchemy as fesa
import inspect
import publicprize.config as ppc
import re
import importlib

_app = flask.Flask(__name__, template_folder=".")
_app.config.from_object(ppc.DevConfig)

db = fesa.SQLAlchemy(_app)

_DEFAULT_ACTION = 'home'
#TODO: BIV_ID needs to be an object
_DEFAULT_BIV_ID = '1004'
_ERROR_BIV_ID = '2004'
_STATIC_BIV_ID = '3004'
_DEFAULT_BIV_URI = 'index.html'
_ERROR_BIV_URI = 'error'

_biv_type_to_task_class= {}
_biv_type_to_model_class= {}

def app():
    return _app

def init():
    "Initialize class maps"
    for n in ['general', 'contest']:
        p = 'publicprize.' + n + '.';
        m = importlib.import_module(p + 'model')
        t = importlib.import_module(p + 'task')
        for cn, c in inspect.getmembers(m, inspect.isclass):
            if hasattr(c, 'BIV_TYPE'):
                _biv_type_to_model_class[c.BIV_TYPE] = c
                _biv_type_to_task_class[c.BIV_TYPE] = getattr(t, cn)
        
@_app.errorhandler(404)
def _error_404(e):
    return _route(_ERROR_BIV_URI + '/' + 'not-found')

@_app.route("/")
def _route_root():
    return _route('')

@_app.route("/<path:path>")
def _route(path):
    # request_context
    biv_id, action, path_info = _parse_path(path)
    # assign path_info, etc. to request_context
    biv_type = biv_id[-3:]
    biv_obj = _load_biv_obj(biv_type, biv_id)
    action_method = _lookup_action(biv_type, action)
    return action_method(biv_obj)

def _load_biv_obj(biv_type, biv_id):
    if not biv_type in _biv_type_to_model_class:
        raise ValueError(biv_type + ": unknown biv_type")
    return _biv_type_to_model_class[biv_type].load_biv(biv_id)

def _lookup_biv_id(biv_uri):
    if len(biv_uri) == 0:
        biv_uri = _DEFAULT_BIV_URI
    m = re.match('^=(\d+)$', biv_uri)
    if m:
        return m.group(1)
    #TODO: will want a static look aside for error lookups at a minimum
    #      but will want db lookups in biv_uri_alias_t
    d = {
        _DEFAULT_BIV_URI: '1004',
        _ERROR_BIV_URI: '2004',
        # flask serves /static implicitly so need to shadow here
        'static': '3004',
    };
    if biv_uri in d:
        return d[biv_uri]

    # Testing not found
    flask.abort(404)

    #TODO: wrap better
    raise ValueError(biv_uri + ': invalid syntax')

def _lookup_action(biv_type, name):
    tc = _biv_type_to_task_class[biv_type]
    name = re.sub('\W', '_', name)
    n = 'action_' + name
    if not hasattr(tc, n):
        raise ValueError(n + ': action not found')
    m = getattr(tc, n)
    if not inspect.isfunction(m):
        raise ValueError(n + ': action not a method')
    return m

def _parse_path(path):
    parts = path.split('/', 2)
    biv_uri = parts[0] if len(parts) >= 1 else _DEFAULT_BIV_URI
    action = parts[1] if len(parts) >= 2 else _DEFAULT_ACTION
    path_info = parts[2] if len(parts) >= 3 else None
    biv_id = _lookup_biv_id(biv_uri)
    return biv_id, action, path_info

class Task(object):
    def __init__(self):
        pass

"""

@_app.route("/")
@_app.route("/index.html")
def home_page():
    return flask.render_template("site_root/index.html")

@_app.route('/<biv_id>/contestants')
def contestants(biv_id):
    return flask.render_template("contest/contestants.html")

@_app.route('/<biv_id>/donors')
def donors(biv_id):
    return flask.render_template("contest/donors.html")

@_app.route('/<biv_id>/about')
def about(biv_id):
    return flask.render_template("contest/about.html")

@_app.route('/<biv_id>/how-to-enter')
def how_to_enter(biv_id):
    return flask.render_template("contest/how-to-enter.html")

@_app.errorhandler(404)
def page_not_found(e):
    return flask.render_template('error/not-found.html'), 404
"""

