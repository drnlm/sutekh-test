# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Plugin for exporting to CSV format"""

import gtk
from sutekh.core.Objects import PhysicalCardSet
from sutekh.io.WriteCSV import WriteCSV
from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.gui.generic.baseplugins.BaseExport import BaseExport


class CardSetExportCSV(SutekhPlugin, BaseExport):
    """Provides a dialog for selecting a filename, then calls on
       WriteCSV to produce the required output."""
    dTableVersions = {PhysicalCardSet: (4, 5, 6)}
    aModelsSupported = (PhysicalCardSet,)

    _dExporters = {
            'CSV': (WriteCSV, 'Export to CSV', '.csv', 'CSV Files', ['*.csv']),
            }

    def _create_dialog(self, tInfo):
        oDlg = super(CardSetExportCSV, self)._create_dialog(tInfo)
        # Add extra widgets for CSV export options
        self.oIncHeader = gtk.CheckButton("Include Column Headers")
        self.oIncHeader.set_active(True)
        oDlg.vbox.pack_start(self.oIncHeader, expand=False)
        self.oIncExpansion = gtk.CheckButton("Include Expansions")
        self.oIncExpansion.set_active(True)
        oDlg.vbox.pack_start(self.oIncExpansion, expand=False)
        oDlg.show_all()
        return oDlg

    def handle_response(self, sFilename, cWriter):
        """Handle the users response. Write the CSV output to file."""
        if sFilename is not None:
            oCardSet = self.get_card_set()
            if not oCardSet:
                return
            oWriter = cWriter(self.oIncHeader.get_active(),
                              self.oIncExpansion.get_active())
            self._write_cardset(sFilename, oWriter, oCardSet)


plugin = CardSetExportCSV
