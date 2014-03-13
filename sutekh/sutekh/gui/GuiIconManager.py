# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""GTK gui icon manager."""

import gtk
import gobject
import os
from sutekh.base.Utility import prefs_dir, ensure_dir_exists
from sutekh.core.SutekhObjects import Creed, DisciplinePair, Virtue, Clan, \
        CardType
from sutekh.io.IconManager import VtESIconManager
from sutekh.base.gui.CachedIconManager import CachedIconManager
from sutekh.base.gui.SutekhDialog import do_complaint


class GuiIconManager(CachedIconManager, VtESIconManager):
    """Gui Manager for the VTES Icons.

       Subclass IconManager to return gtk pixbufs, not filenames.
       Also provides gui interfaces for setup and downloading icons.
       """

    def __init__(self, sPath):
        if not sPath:
            sPath = os.path.join(prefs_dir('Sutekh'), 'icons')
        super(GuiIconManager, self).__init__(sPath)

    def setup(self):
        """Prompt the user to download the icons if the icon directory
           doesn't exist"""
        if os.path.lexists(self._sPrefsDir):
            # We accept broken links as stopping the prompt
            if os.path.lexists("%s/clans" % self._sPrefsDir):
                return
            else:
                # Check if we need to upgrade to the V:EKN icons
                ensure_dir_exists("%s/clans" % self._sPrefsDir)
                if os.path.exists('%s/IconClanAbo.gif' % self._sPrefsDir):
                    iResponse = do_complaint(
                            "Sutekh has switched to using the icons from the "
                            "V:EKN site.\nIcons won't work until you "
                            "re-download them.\n\nDownload icons?",
                            gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO, False)
                else:
                    # Old icons not present, so skip
                    return
        else:
            # Create directory, so we don't prompt next time unless the user
            # intervenes
            ensure_dir_exists(self._sPrefsDir)
            ensure_dir_exists("%s/clans" % self._sPrefsDir)
            # Ask the user if he wants to download
            iResponse = do_complaint("Sutekh can download icons for the cards "
                    "from the V:EKN site\nThese icons will be stored in "
                    "%s\n\nDownload icons?" % self._sPrefsDir,
                    gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO, False)
        if iResponse == gtk.RESPONSE_YES:
            self.download_icons()
        else:
            # Let the user know about the other options
            do_complaint("Icon download skipped.\nYou can choose to download "
                    "the icons from the File menu.\nYou will not be prompted "
                    "again unless you delete %s" % self._sPrefsDir,
                    gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, False)

    def _get_icon_total(self):
        """Return the total number of icons"""
        return (Creed.select().count() +
                DisciplinePair.select().count() + Clan.select().count() +
                Virtue.select().count() + CardType.select().count() + 2)
