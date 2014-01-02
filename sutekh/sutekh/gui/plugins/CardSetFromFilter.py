# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Converts a filter into a card set"""

from sutekh.core.Objects import PhysicalCardSet, PhysicalCard
from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.gui.generic.baseplugins.BaseCSFromFilter import BaseCSFromFilter


class DeckFromFilter(SutekhPlugin, BaseCSFromFilter):
    """Converts a filter into a Card Set."""

    dTableVersions = {PhysicalCardSet: (4, 5, 6)}
    aModelsSupported = (PhysicalCardSet, PhysicalCard)


plugin = DeckFromFilter
