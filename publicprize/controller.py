# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import publicprize.biv_uri as ppbu
import flask
import flask.ext.sqlalchemy as fesa
import importlib
import inspect
import publicprize.config as ppc
import re

db = None

def app():
    return _app

def init():
    """Initialize class maps.

    Must be done externally, because of circular import from
    components.
    """
    for pkg in ['general', 'contest']:
        p = 'publicprize.' + pkg + '.';
        m = importlib.import_module(p + 'model')
        t = importlib.import_module(p + 'task')
        for cn, c in inspect.getmembers(m, inspect.isclass):
            if issubclass(c, Model):
                _biv_id_marker_to_model_class[c.BIV_ID_MARKER] = c
                _biv_id_marker_to_task_class[c.BIV_ID_MARKER] = getattr(t, cn)
        
class Task(object):

    def __init__(self):
        pass

class Model(object):

    @classmethod
    def load_biv_obj(cls, biv_id):
        return cls.query.filter_by(biv_id=biv_id).first_or_404()

def _init():
    global _ACTION_METHOD_PREFIX
    global _DEFAULT_ACTION_NAME
    global _DEFAULT_BIV_URI
    global _ERROR_BIV_URI
    global _app
    global _biv_alias_to_biv_id
    global _biv_id_marker_to_model_class
    global _biv_id_marker_to_task_class
    global db

    _app = flask.Flask(__name__, template_folder=".")
    _app.config.from_object(ppc.DevConfig)
    db = fesa.SQLAlchemy(_app)

    _ACTION_METHOD_PREFIX = 'action_'
    _DEFAULT_BIV_URI = 'index'
    _ERROR_BIV_URI = 'error'
    _DEFAULT_ACTION_NAME = _DEFAULT_BIV_URI
    _biv_id_marker_to_task_class= {}
    _biv_id_marker_to_model_class= {}
    _biv_alias_to_biv_id = {
        #TODO: get from general module
        _DEFAULT_BIV_URI: '1001',
        _ERROR_BIV_URI: '2001',
        # flask serves /static implicitly so need to shadow here
        'static': '3001'}

_init()

def _load_biv_obj(biv_id_marker, biv_id):
    if not biv_id_marker in _biv_id_marker_to_model_class:
        raise ValueError(biv_id_marker + ": unknown biv_id_marker")
    return _biv_id_marker_to_model_class[biv_id_marker].load_biv_obj(biv_id)

def _lookup_action(biv_id_marker, name):
    if len(name) == 0:
        name = _DEFAULT_ACTION_NAME
    task = _biv_id_marker_to_task_class[biv_id_marker]
    name = re.sub('\W', '_', name)
    name = _ACTION_METHOD_PREFIX + name

    if not hasattr(task, name):
        raise ValueError(name + ': action not found')
    m = getattr(task, name)
    if not inspect.isfunction(m):
        raise ValueError(name + ': action not a method')
    return m

def _lookup_biv_id(biv_uri):
    if len(biv_uri) == 0:
        biv_uri = _DEFAULT_BIV_URI
    elif ppbu.is_encoded(biv_uri):
        return ppbu.to_biv_id(biv_uri)

    if biv_uri in _biv_alias_to_biv_id:
        return _biv_alias_to_biv_id[biv_uri]

    # Test not found action, but want better exception
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
    biv_id_marker = biv_id[-3:]
    biv_obj = _load_biv_obj(biv_id_marker, biv_id)
    action_method = _lookup_action(biv_id_marker, action)
    return action_method(biv_obj)

@_app.errorhandler(404)
def _route_404(e):
    return _route(_ERROR_BIV_URI + '/' + 'not-found')

@_app.route("/")
def _route_root():
    return _route('')
