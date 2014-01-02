# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2010 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details
"""Create a snapshot of the current card set."""

from sutekh.core.Objects import PhysicalCardSet
from sutekh.gui.generic.baseplugins.BaseSnapshot import BaseSnapshot
from sutekh.gui.PluginManager import SutekhPlugin


class SnapshotCardSet(SutekhPlugin, BaseSnapshot):
    """Creates a snapshot of the card set.

       The snapshot is a copy of the current state of the card set, with the
       date and time appended to the name, and it is a child of the card set.
       """

    dTableVersions = {PhysicalCardSet: (6,)}
    aModelsSupported = (PhysicalCardSet,)


plugin = SnapshotCardSet
