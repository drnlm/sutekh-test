# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2008, 2009 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Plugin for exporting to standard writers"""

import gtk
from ....core.generic.CardSetHolder import CardSetWrapper
from ..BasePluginManager import BasePlugin
from ..SutekhFileWidget import ExportDialog
from ..SutekhDialog import do_exception_complaint
from ....generic.Utility import safe_filename


class BaseExport(BasePlugin):
    """Provides a dialog for selecting a filename, then calls on
       the appropriate writer to produce the required output.
       
       Subclasses should fill in _dExporters as appropriate."""

    _dExporters = {
            # sKey : (writer, menu name, extension, [filter name,
            #         [filter patterns]], [filter name, [patterns]])
            # Filter name & pattern are optional, and default to
            # 'Text files', '*.txt' if not present
            # Extension is directly appended to suggested filename,
            # so should include an initial . if appropriate
            }

    def get_menu_item(self):
        """Register with the 'Export Card Set' Menu"""
        if not self.check_versions() or not self.check_model_type():
            return None
        aMenuItems = []
        for sKey, tInfo in self._dExporters.iteritems():
            sMenuText = tInfo[1]
            oExport = gtk.MenuItem(sMenuText)
            oExport.connect("activate", self.run_dialog, sKey)
            aMenuItems.append(('Export Card Set', oExport))
        return aMenuItems

    def _create_dialog(self, tInfo):
        """Construct the dialog.

           Subclasses can override this if they need custom behavior"""
        sSuggestedFileName = '%s%s' % (safe_filename(self.view.sSetName),
            tInfo[2])
        oDlg = ExportDialog("Choose FileName for Exported CardSet",
                self.parent, sSuggestedFileName)
        if len(tInfo) > 3:
            for sName, aPattern in zip(tInfo[3::2], tInfo[4::2]):
                oDlg.add_filter_with_pattern(sName, aPattern)
        else:
            oDlg.add_filter_with_pattern('Text Files', ['*.txt'])
        return oDlg

    def run_dialog(self, _oWidget, sKey):
        """Create & Execute the dialog"""
        tInfo = self._dExporters[sKey]
        oDlg = self._create_dialog(tInfo)
        oDlg.run()
        self.handle_response(oDlg.get_name(), tInfo[0])

    def _write_cardset(self, sFilename, oWriter, oCardSet):
        """Actually commit the card set"""
        try:
            fOut = file(sFilename, "w")
            oWriter.write(fOut, CardSetWrapper(oCardSet))
            fOut.close()
        except IOError, oExp:
            do_exception_complaint("Failed to open output file.\n\n%s" % oExp)

    def handle_response(self, sFilename, cWriter):
        """Handle the users response. Write the text output to file."""
        if sFilename is not None:
            oCardSet = self.get_card_set()
            if not oCardSet:
                return
            oWriter = cWriter()
            self._write_cardset(sFilename, oWriter, oCardSet)
