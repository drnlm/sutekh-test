# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2007 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Cache various objects to speed up database queries."""

from ..Objects import CACHE_LIST, init_cache


class ObjectCache(object):
    """Holds references to commonly used database objects so that they don't
       get removed from the cache during big reads.
       """

    def __init__(self):
        self._dCache = {}
        for cType in CACHE_LIST:
            self._dCache[cType] = list(cType.select())

        init_cache()
