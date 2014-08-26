# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

from .. import biv
from .. import controller as ppc

class General(ppc.Model):

    def __init__(self, biv_id):
        super().__init__()
        self._biv_id = biv_id

    def load_biv_obj(biv_id):
        return General(biv_id)

_BIV_MARKER = biv.register_marker(1, General)
biv.register_alias(biv.URI_FOR_NONE, _BIV_MARKER.to_id(1))
biv.register_alias(biv.URI_FOR_ERROR, _BIV_MARKER.to_id(2))
biv.register_alias(biv.URI_FOR_STATIC_FILES, _BIV_MARKER.to_id(3))
