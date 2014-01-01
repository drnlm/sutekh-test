# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Classes for managing and creating plugins for Sutekh."""

import sutekh.gui.plugins as plugins
from sutekh.gui.generic.BasePluginManager import (BasePluginManager,
        PluginConfigFileListener, BasePlugin)


class SutekhPlugin(BasePlugin):
    """Base class for sutekh plugins."""


class PluginManager(BasePluginManager):
    """Manages plugins for Sutekh

       Plugin modules should be placed in the plugins package directory and
       contain an attribute named 'plugin' which points to the plugin class the
       module contains.
       """

    def load_plugins(self):
        """Load list of Plugin Classes from plugin dir."""
        self._do_load_plugins('sutekh', plugins, SutekhPlugin)
