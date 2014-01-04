# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2007 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Export a card set to HTML."""

import gtk
from sutekh.core.Objects import PhysicalCardSet
from sutekh.io.WriteArdbHTML import WriteArdbHTML
from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.gui.generic.baseplugins.BaseExport import BaseExport


class CardSetExportHTML(SutekhPlugin, BaseExport):
    """Export a Card set to a 'nice' HTML file.

       We create a ElementTree that represents the XHTML file,
       and then dump that to file.
       This tries to match the HTML file produced by ARDB.
       """
    dTableVersions = {PhysicalCardSet: (4, 5, 6)}
    aModelsSupported = (PhysicalCardSet, "MainWindow")

    dGlobalConfig = {
        'HTML export mode': 'string(default=None)',
    }

    _dExporters = {
            "HTML": (WriteArdbHTML, "Export to HTML", 
                     '.html', 'HTML Files', ['*.html']),
            }


    def get_menu_item(self):
        """Register on the correct Menu"""
        if not self.check_versions() or not self.check_model_type():
            return None

        if self._cModelType == "MainWindow":
            oPrefs = gtk.MenuItem("Export to HTML preferences")
            oSubMenu = gtk.Menu()
            oPrefs.set_submenu(oSubMenu)
            oGroup = None
            sDefault = self.get_config_item('HTML export mode')
            if sDefault is None:
                sDefault = 'Secret Library'
                self.set_config_item('HTML export mode',
                        sDefault)
            for sString, sVal in (("Add links to The Secret Library",
                'Secret Library'),
                    ("Add links to VTES Monger", 'Monger'),
                    ("Don't add links in the HTML file", 'None')):
                oItem = gtk.RadioMenuItem(oGroup, sString)
                if not oGroup:
                    oGroup = oItem
                oSubMenu.add(oItem)
                oItem.set_active(False)
                if sVal == sDefault:
                    oItem.set_active(True)
                oItem.connect("toggled", self.change_prefs, sVal)
            return ('File Preferences', oPrefs)

        return super(CardSetExportHTML, self).get_menu_item()

    def change_prefs(self, _oWidget, sChoice):
        """Manage the preferences (library to link to, etc.)"""
        sCur = self.get_config_item('HTML export mode')
        if sChoice != sCur:
            self.set_config_item('HTML export mode',
                    sChoice)

    # pylint: disable-msg=W0201
    # we define attributes outside __init__, but it's OK because of plugin
    # structure
    def _create_dialog(self, tInfo):
        """Create the dialog prompting for the filename."""
        oDlg = super(CardSetExportHTML, self)._create_dialog(tInfo)
        # pylint: disable-msg=E1101
        # vbox confuses pylint
        self.oTextButton = gtk.CheckButton("Include Card _Texts?")
        self.oTextButton.set_active(False)
        oDlg.vbox.pack_start(self.oTextButton, False, False)
        oDlg.show_all()
        return oDlg

    # pylint: enable-msg=W0201

    def handle_response(self, sFilename, _cWriter):
        """Handle the response to the dialog"""
        # pylint: disable-msg=E1101
        # SQLObject methods confuse pylint
        if sFilename is not None:
            # pylint: disable-msg=W0703
            # we do want to catch all exceptions here
            oCardSet = self.get_card_set()
            if not oCardSet:
                return
            bDoText = False
            if self.oTextButton.get_active():
                bDoText = True
            sLinkMode = self.get_config_item('HTML export mode')
            oWriter = WriteArdbHTML(sLinkMode, bDoText)
            self._write_cardset(sFilename, oWriter, oCardSet)


plugin = CardSetExportHTML
