# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2011 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Plugin for displaying the exported version of a card set in a gtk.TextView.
   Intended to make cutting and pasting easier."""

from sutekh.core.Objects import PhysicalCardSet
from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.gui.generic.baseplugins.BaseShowExported import BaseShowExported
from sutekh.io.WriteJOL import WriteJOL
from sutekh.io.WriteLackeyCCG import WriteLackeyCCG
from sutekh.io.WriteELDBDeckFile import WriteELDBDeckFile
from sutekh.io.WriteArdbText import WriteArdbText
from sutekh.io.WritePmwiki import WritePmwiki
from sutekh.io.WriteVEKNForum import WriteVEKNForum
from sutekh.io.WriteCSV import WriteCSV


class ShowExported(SutekhPlugin, BaseShowExported):
    """Display the various exported versions of a card set for sutekh.

       Provides the most commonly pasted formats.
       """

    dTableVersions = {}
    aModelsSupported = (PhysicalCardSet,)

    _dExporters = {
            # radio button text : Writer
            'Export to JOL format': WriteJOL,
            'Export to Lackey CCG format': WriteLackeyCCG,
            'Export to ARDB Text': WriteArdbText,
            'BBcode output for the V:EKN Forums': WriteVEKNForum,
            'Export to ELDB ELD Deck File': WriteELDBDeckFile,
            'CSV Export (with headers)': WriteCSV,
            'Export to pmwiki': WritePmwiki,
            }


plugin = ShowExported
