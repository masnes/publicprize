# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import flask
import flask.ext.sqlalchemy as fesa
import inspect
import publicprize.config as ppc
import re
import importlib

db = None

def app():
    return _app

def init():
    """Initialize class maps.

    Must be done externally, because of circular import from
    components.
    """
    global _biv_type_to_model_class
    global _biv_type_to_task_class
    for pkg in ['general', 'contest']:
        p = 'publicprize.' + pkg + '.';
        m = importlib.import_module(p + 'model')
        t = importlib.import_module(p + 'task')
        for cn, c in inspect.getmembers(m, inspect.isclass):
            if issubclass(c, Model):
                _biv_type_to_model_class[c.BIV_TYPE] = c
                _biv_type_to_task_class[c.BIV_TYPE] = getattr(t, cn)
        
class Task(object):

    def __init__(self):
        pass

class Model(object):

    @classmethod
    def load_biv_obj(cls, biv_id):
        cls.query.filter_by(biv_id=biv_id).first_or_404()

def _init():
    global _app
    global db
    global _biv_type_to_task_class
    global _biv_type_to_model_class
    global _DEFAULT_BIV_URI
    global _ERROR_BIV_URI
    global _DEFAULT_ACTION_NAME

    _app = flask.Flask(__name__, template_folder=".")
    _app.config.from_object(ppc.DevConfig)
    db = fesa.SQLAlchemy(_app)

    _DEFAULT_BIV_URI = 'index'
    _ERROR_BIV_URI = 'error'
    _DEFAULT_ACTION_NAME = _DEFAULT_BIV_URI
    _biv_type_to_task_class= {}
    _biv_type_to_model_class= {}

_init()

def _load_biv_obj(biv_type, biv_id):
    print(_biv_type_to_model_class)
    if not biv_type in _biv_type_to_model_class:
        raise ValueError(biv_type + ": unknown biv_type")
    return _biv_type_to_model_class[biv_type].load_biv_obj(biv_id)

def _lookup_action(biv_type, name):
    if len(name) == 0:
        name = _DEFAULT_ACTION_NAME
    tc = _biv_type_to_task_class[biv_type]
    name = re.sub('\W', '_', name)
    n = 'action_' + name
    if not hasattr(tc, n):
        raise ValueError(n + ': action not found')
    m = getattr(tc, n)
    if not inspect.isfunction(m):
        raise ValueError(n + ': action not a method')
    return m

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

def _parse_path(path):
    parts = path.split('/', 2)
    biv_uri = parts[0] if len(parts) >= 1 else _DEFAULT_BIV_URI
    action = parts[1] if len(parts) >= 2 else _DEFAULT_ACTION_NAME
    path_info = parts[2] if len(parts) >= 3 else None
    biv_id = _lookup_biv_id(biv_uri)
    return biv_id, action, path_info

@_app.route("/<path:path>")
def _route(path):
    # request_context
    biv_id, action, path_info = _parse_path(path)
    # assign path_info, etc. to request_context
    biv_type = biv_id[-3:]
    biv_obj = _load_biv_obj(biv_type, biv_id)
    action_method = _lookup_action(biv_type, action)
    return action_method(biv_obj)

@_app.errorhandler(404)
def _route_404(e):
    return _route(_ERROR_BIV_URI + '/' + 'not-found')

@_app.route("/")
def _route_root():
    return _route('')

