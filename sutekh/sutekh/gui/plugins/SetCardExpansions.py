# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2007 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details
"""Force all cards which can only belong to 1 expansion to that expansion"""

from sutekh.core.Objects import PhysicalCardSet
from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.gui.generic.baseplugins.BaseSetExpansions import BaseSetExpansions


class SetCardExpansions(SutekhPlugin, BaseSetExpansions):
    """Set al the selected cards in the card list to a single expansion

       Find the common subset of expansions for the selected list, and allow
       the user to choose which expansion to set all the cards too.
       """

    dTableVersions = {PhysicalCardSet: (5, 6)}
    aModelsSupported = (PhysicalCardSet,)


plugin = SetCardExpansions
