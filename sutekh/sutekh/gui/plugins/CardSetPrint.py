# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2007 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Plugin for simple, direct printing of the card set."""


from sutekh.core.Objects import PhysicalCardSet
from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.gui.generic.baseplugins.BaseCardSetPrint import BaseCardSetPrint


class CardSetPrint(SutekhPlugin, BaseCardSetPrint):
    """Plugin for printing the card sets.

       Use gtk's Printing support to print out a simple list of the cards
       in the card set. This has less formatting than exporting via
       HTML, for instance, but does print directly.
       """
    dTableVersions = {PhysicalCardSet: (4, 5, 6)}
    aModelsSupported = (PhysicalCardSet,)


plugin = CardSetPrint
