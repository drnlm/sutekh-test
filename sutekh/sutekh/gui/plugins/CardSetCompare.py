# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Simon Cross <hodgestar@gmail.com>,
# Copyright 2006, 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details
"""Compare the contents of two card sets"""

from sutekh.core.Objects import PhysicalCardSet
from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.gui.generic.baseplugins.BaseCardSetCompare import BaseCardSetCompare


class CardSetCompare(SutekhPlugin, BaseCardSetCompare):
    """Compare Two Card Sets

       Display a gtk.Notebook containing tabs for common cards, and cards
       only in each of the card sets.
       """
    dTableVersions = {PhysicalCardSet: (5, 6)}
    aModelsSupported = (PhysicalCardSet,)


plugin = CardSetCompare
