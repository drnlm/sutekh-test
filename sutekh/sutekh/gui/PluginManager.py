# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Specialise plugin classes for Sutekh."""

import sutekh.gui.plugins as plugins
from sutekh.base.gui.BasePluginManager import BasePluginManager, BasePlugin


class PluginManager(BasePluginManager):
    """Manages plugins for Sutekh"""

    def __init__(self):
        super(PluginManager, self).__init__()
        self._cPluginBase = SutekhPlugin
        self._sModule = "sutekh.gui.plugins"

    def load_plugins(self):
        self._do_load_plugins(plugins)


class SutekhPlugin(BasePlugin):
    pass
