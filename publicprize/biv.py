# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.
"""biv operations: converting to/from uri's.  Loading objects, etc.
"""
import inspect
import numconv

URI_FOR_NONE = 'index'
URI_FOR_ERROR = 'error'
URI_FOR_STATIC_FILES = 'static'

class Id(int):
    def __new__(cls, biv_id):
        if isinstance(biv_id, cls):
            return biv_id
        biv_id = int(biv_id)
        assert _MARKER_MODULUS < biv_id <= _MAX_ID
        return super().__new__(cls, biv_id)

class Marker(int):
    def __new__(cls, biv_marker):
        if isinstance(biv_marker, cls):
            return biv_marker
        biv_marker = int(biv_marker)
        assert 0 < biv_marker <= _MAX_MARKER
        return super().__new__(cls, biv_marker)

    def to_id(self, bix):
        """Convert an index value to a biv_id
        """
        return _join(_assert_bix(bix), self.__int__())

class URI(str):
    def __new__(cls, uri):
        return super().__new__(cls, uri)

def id_to_uri(biv_id, use_alias=True):
    """Converts a biv_id to a biv_uri.

    Args:
        biv_id (int): to be converted

    Returns:
        str: biv_uri

    Raises:
        ValueError: if biv_id is not parseable
    """
    if use_alias and biv_id in _id_to_alias:
        return _id_to_alias[biv_id][0]
    bix, bm = _split(biv_id)
    bm = _CONV.int2str(bm).zfill(_MARKER_ENC_LEN)
    bix = _CONV.int2str(bix)
    return URI(_ENC_PREFIX + bix + bm)

def register_alias(uri, biv_id):
    """Registers biv_id with uri

    Args:
        uri (str): must be globally unique
        biv_id (int): what's identified
        
    Returns:
        str: uri
    """
    biv_id = Id(biv_id)
    assert not uri in _alias_to_id
    assert not uri[0] == _ENC_PREFIX
    _alias_to_id[uri] = biv_id
    if not biv_id in _id_to_alias:
        _id_to_alias[biv_id] = []
    _id_to_alias[biv_id].append(uri)
    return uri
    
def register_marker(biv_marker, cls):
    """Registers a marker in a global table for a model, which
    can load_biv_obj

    Args:
        biv_marker (int): marker

    Returns:
        Marker: used for generating idempotent id sequences (special case)

    Asserts:
        if duplicate or invalid function
    """
    biv_marker = Marker(biv_marker)
    assert _has_method(cls, 'load_biv_obj')
    assert not biv_marker in _marker_to_class
    _marker_to_class[biv_marker] = cls
    return Marker(biv_marker)

def load_obj(biv_uri, use_alias=True):
    """Loads an object for the specified biv_uri

    Args:
        biv_uri (str): identify of obj

    Returns:
        object: biv_obj
    """
    if biv_uri is None or len(biv_uri) == 0:
        biv_uri = URI_FOR_NONE
    if use_alias and biv_uri in _alias_to_id:
        biv_id = _alias_to_id[biv_uri]
        bix, bm = _split(biv_id)
    else:
        bix, bm = _decode_uri(biv_uri)
        biv_id = _join(bix, bm)
    return _marker_to_class[bm].load_biv_obj(biv_id)

def _assert_bix(bix):
    bix = int(bix)
    assert 0 < bix <= _MAX_BIX
    return bix

def _decode_uri(biv_uri):
    assert biv_uri[0] == _ENC_PREFIX
    biv_uri = biv_uri[1:]
    if len(biv_uri) < _MARKER_ENC_LEN:
        raise ValueError(biv_uri + ': biv_uri too short')
    bm = Marker(_CONV.str2int(biv_uri[-_MARKER_ENC_LEN:]))
    bix = _assert_bix(_CONV.str2int(biv_uri[:-_MARKER_ENC_LEN]))
    return (bix, bm)

def _join(bix, bm):
    return bix * _MARKER_MODULUS + bm

def _has_method(cls, method):
    for c in inspect.getmro(cls):
        if hasattr(c, method) and inspect.ismethod(getattr(c, method)):
            return True
    return False

def _split(biv_id):
    biv_id = Id(biv_id)
    bm = Marker(biv_id % _MARKER_MODULUS)
    bix = biv_id // _MARKER_MODULUS
    return (bix, bm)
    
_CONV = numconv.NumConv(radix=62, alphabet=numconv.BASE62)
_ENC_PREFIX = '_'
_IDEMPOTENT_URI = None
_MARKER_MODULUS = 1000
_MAX_ID = int(10e18) - 1
_MAX_BIX = _MAX_ID // _MARKER_MODULUS
# We reserve 900 and above for versioning and growth
_MAX_MARKER = _MARKER_MODULUS - 101
_MARKER_ENC_LEN = len(_CONV.int2str(_MAX_MARKER))
_marker_to_class = {}
_alias_to_id = {}
_id_to_alias = {}
