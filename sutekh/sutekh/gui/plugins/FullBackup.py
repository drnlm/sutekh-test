# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2007 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details
"""Plugin to wrap zipfile backup and restore methods"""

from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.gui.generic.baseplugins.BaseBackup import BaseBackup


class FullBackup(SutekhPlugin, BaseBackup):
    """Provide access to ZipFileWrapper's backup and restore methods.

       Handle GUI aspects associated with restoring (ensuring everything
       reloads, etc.)
       """

    dTableVersions = {}
    aModelsSupported = ("MainWindow",)


plugin = FullBackup
