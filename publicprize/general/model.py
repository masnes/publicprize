# Copyright (c) 2014 bivio Software, Inc.  All rights reserved.

import publicprize.controller as ppc

class General(ppc.Model):
    BIV_ID_MARKER = '001'

    def load_biv_obj(biv_id):
        return General()
