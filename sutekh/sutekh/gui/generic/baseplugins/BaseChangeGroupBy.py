# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Allow the use to change how the cards are grouped in the CardListView"""

from ..BasePluginManager import BasePlugin


class BaseGroupCardList(BasePlugin):
    """Base for plugin to allow the user to change how cards are grouped.

       Subclasses should fill in the GROUPINGS dict and provide config
       file support by setting dPerPaneConfig correctly
       """

    GROUPINGS = {}

    GROUP_BY = "group by"

    dPerPaneConfig = {}

    dCardListConfig = dPerPaneConfig

    # pylint: disable-msg=W0142
    # ** magic OK here
    def __init__(self, *aArgs, **kwargs):
        super(BaseGroupCardList, self).__init__(*aArgs, **kwargs)
        self._oFirstBut = None  # placeholder for the radio group
        # We don't reload on init, to avoid double loads.
        self.perpane_config_updated(False)

    # Config Update

    def perpane_config_updated(self, bDoReload=True):
        """Called by base class on config updates."""
        # bReload flag so we can call this during __init__
        sGrping = self.get_perpane_item(self.GROUP_BY)
        cGrping = self.GROUPINGS.get(sGrping)
        if cGrping is not None:
            self.set_grouping(cGrping, bDoReload)

    # Actions

    def set_grouping(self, cGrping, bReload=True):
        """Set the grouping to that specified by cGrping."""
        if self.model.groupby != cGrping:
            self.model.groupby = cGrping
            if bReload:
                # Use view.load so we get busy cursor, etc.
                self.view.frame.queue_reload()
