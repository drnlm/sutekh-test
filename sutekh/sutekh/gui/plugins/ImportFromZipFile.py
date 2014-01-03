# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details
"""Plugin to import selected card sets from a zip file"""

from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.gui.generic.baseplugins.BaseZipImport import BaseImportFromZipFile


class ImportFromZipFile(SutekhPlugin, BaseImportFromZipFile):
    """Extract selected card sets from a zip file."""

    dTableVersions = {}
    aModelsSupported = ("MainWindow",)


plugin = ImportFromZipFile
