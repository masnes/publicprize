# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.
"""Convert biv_uri to/from biv_id's
"""
import numconv

def from_biv_id(biv_id):
    """Converts a biv_id to a biv_uri.

    Args:
        biv_id (str): to be converted

    Returns:
        str: biv_uri

    Raises:
        ValueError: if biv_id is not parseable
    """
    biv_id = int(biv_id)
    bim = biv_id % _MARKER_MODULUS
    if not 0 < bim <= _MAX_MARKER:
        raise ValueError(bim + ': biv_id_marker outside range')
    if bix == 0:
        raise ValueError(bix + ': biv_id_index outside range')
    bim = _CONV.int2str(bim).zfill(_MARKER_ENC_LEN)
    bix = _CONV.int2str(bix)
    return _ENC_PREFIX + bix + bim

def to_biv_id(biv_uri_enc):
    """Converts an encoded biv_uri to a biv_id.

    Args:
        biv_uri_enc (str): to be converted

    Returns:
        str: biv_id

    Raises:
        ValueError: if biv_uri is not parseable
    """
    assert biv_uri_enc[0] == _ENC_PREFIX
    biv_uri_enc = biv_uri_enc[1:]
    if len(biv_uri_enc) < _MARKER_ENC_LEN:
        raise ValueError(biv_uri_enc + ': biv_uri_enc too short')
    bim = _CONV.str2int(biv_uri_enc[-_MARKER_ENC_LEN:])
    if not 0 < bim <= _MAX_MARKER:
        raise ValueError(str(bim) + ': biv_id_marker outside range')
    bix = _CONV.str2int(biv_uri_enc[:-_MARKER_ENC_LEN])
    if bix == 0:
        raise ValueError(str(bix) + ': biv_id_index outside range')
    return str(bix * _MARKER_MODULUS + bim)

def is_encoded(biv_uri_enc):
    """Is this an encoded uri?

    Args:
        biv_uri_enc (str): to test if encoded uri

    Returns:
        bool: True if encoded uri
    """
    return len(biv_uri_enc) and biv_uri_enc[0] == _ENC_PREFIX

    
_CONV = numconv.NumConv(radix=62, alphabet=numconv.BASE62)
_ENC_PREFIX = '='
_MARKER_MODULUS = 1000
_MAX_MARKER = _MARKER_MODULUS - 101
_MARKER_ENC_LEN = len(_CONV.int2str(_MAX_MARKER))
