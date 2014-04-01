# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Handle the multi pane UI for Sutkeh
# Copyright 2007, 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - See COPYING for details

"""Main window for Sutekh."""

# pylint: disable-msg=C0302
# C0302 - the module is long, but keeping the everything together is the best
# option for now

import pygtk
pygtk.require('2.0')
import gtk
import logging
# pylint: disable-msg=E0611
# pylint doesn't see resource_stream here, for some reason
from pkg_resources import resource_stream, resource_exists
# pylint: enable-msg=E0611
from sqlobject import SQLObjectNotFound
from sutekh.base.core.DBUtility import flush_cache
from sutekh.base.core.BaseObjects import IAbstractCard
from sutekh.core.SutekhObjectCache import SutekhObjectCache
from sutekh.core.Filters import make_illegal_filter, best_guess_filter
from sutekh.io.XmlFileHandling import PhysicalCardSetXmlFile
from sutekh.gui.CardTextFrame import CardTextFrame
from sutekh.gui.AboutDialog import SutekhAboutDialog
from sutekh.gui.MainMenu import MainMenu
from sutekh.gui.PluginManager import PluginManager
from sutekh.gui.GuiDBManagement import refresh_ww_card_list
from sutekh.gui import SutekhIcon
from sutekh.base.gui.AppMainWindow import AppMainWindow
from sutekh.gui.GuiIconManager import GuiIconManager
from sutekh.base.gui.SutekhDialog import do_complaint


class SutekhMainWindow(AppMainWindow):
    """Main window for Sutekh."""
    # pylint: disable-msg=R0904, R0902
    # R0904 - gtk.Widget, so many public methods
    # R0902 - we need to keep a lot of state, so many instance attributes
    def __init__(self):
        super(SutekhMainWindow, self).__init__(PhysicalCardSetXmlFile,
                                               make_illegal_filter,
                                               best_guess_filter)
        # We can shrink the window quite small
        self.set_size_request(100, 100)
        # But we start at a reasonable size
        self.set_default_size(800, 600)

        # Set Default Window Icon for all Windows
        gtk.window_set_default_icon(SutekhIcon.SUTEKH_ICON)

        self._oSutekhObjectCache = None

    def _verify_database(self):
        """Check database is correctly populated"""
        try:
            _oCard = IAbstractCard('Ossian')
        except SQLObjectNotFound:
            # Log error so verbose picks it up
            logging.warn('Ossian not found in the database')
            # Inform the user
            iResponse = do_complaint(
                    'Database is missing cards. Try import the cardlist now?',
                    gtk.MESSAGE_ERROR, gtk.BUTTONS_YES_NO, False)
            if iResponse == gtk.RESPONSE_YES:
                refresh_ww_card_list(self)

        # Create object cache
        self._oSutekhObjectCache = SutekhObjectCache()

    # pylint: disable-msg=W0201
    # We define attributes here, since this is called after database checks
    def setup(self, oConfig):
        """After database checks are passed, setup what we need to display
           data from the database."""
        oPluginManager = PluginManager()
        oIconManager = GuiIconManager(oConfig.get_icon_path())
        oCardTextPane = CardTextFrame(self, oIconManager)

        super(SutekhMainWindow, self).setup(oConfig, oCardTextPane,
                                             oIconManager, oPluginManager)

    def _create_app_menu(self):
        """Create the main application menu."""
        self._oMenu = MainMenu(self, self._oConfig)
                    
    # pylint: enable-msg=W0201

    def update_to_new_db(self):
        """Resync panes against the database.

           Needed because ids aren't kept across re-reading the WW
           cardlist, since card sets with children are always created
           before there children are added.
           """
        # Flush the caches, so we don't hit stale lookups
        flush_cache()
        # Reset the lookup cache holder
        self._oSutekhObjectCache = SutekhObjectCache()
        # We publish here, after we've cleared the caches
        super(SutekhMainWindow, self).update_to_new_db()

    def clear_cache(self):
        """Remove the cached set of objects, for card list reloads, etc."""
        del self._oSutekhObjectCache

    def show_about_dialog(self, _oWidget):
        """Display the about dialog"""
        oDlg = SutekhAboutDialog()
        oDlg.run()
        oDlg.destroy()

    # pylint: disable-msg=R0201
    # Making this a function would not be convenient
    def _link_resource(self, sLocalUrl):
        """Return a file-like object which sLocalUrl can be read from."""
        sResource = '/docs/html/%s' % sLocalUrl
        if resource_exists('sutekh', sResource):
            return resource_stream('sutekh', sResource)
        else:
            raise ValueError("Unknown resource %s" % sLocalUrl)

    # pylint: enable-msg=R0201

    def show_tutorial(self, _oMenuWidget, oHelpLast):
        """Show the HTML Tutorial"""
        self._do_html_dialog("Tutorial.html", oHelpLast)

    def show_manual(self, _oMenuWidget, oHelpLast):
        """Show the HTML Manual"""
        self._do_html_dialog("Manual.html", oHelpLast)
