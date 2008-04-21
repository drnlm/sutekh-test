# CSVImporter.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Simon Cross <hodgestar@gmail.com>,
# GPL - see COPYING for details

import gtk
import csv
import gobject
from sutekh.io.CSVParser import CSVParser
from sutekh.core.SutekhObjects import PhysicalCard, AbstractCardSet, PhysicalCardSet
from sutekh.core.CardLookup import LookupFailed
from sutekh.gui.PluginManager import CardListPlugin
from sutekh.gui.SutekhDialog import SutekhDialog, do_complaint_error
from sutekh.gui.SutekhFileWidget import SutekhFileButton

class CSVImporter(CardListPlugin):
    dTableVersions = {
        AbstractCardSet: [3],
        PhysicalCardSet: [4],
        PhysicalCard: [2],
    }
    aModelsSupported = [AbstractCardSet, PhysicalCardSet, PhysicalCard]

    def __init__(self,*args,**kws):
        super(CSVImporter,self).__init__(*args,**kws)
        self._dCSVImportDestinations = {
            'Physical Cards': (CSVParser.PCL, None),
            'Physical Card Set': (CSVParser.PCS, PhysicalCardSet),
            'Abstract Card Set': (CSVParser.ACS, AbstractCardSet),
        }

    def get_menu_item(self):
        """
        Overrides method from base class.
        """
        if not self.check_versions() or not self.check_model_type():
            return None
        iDF = gtk.MenuItem("Import CSV File")
        iDF.connect("activate", self.activate)
        return iDF

    def get_desired_menu(self):
        return "Plugins"

    def activate(self,oWidget):
        oDlg = self.make_dialog()
        oDlg.run()

    def make_dialog(self):
        self.oDlg = SutekhDialog("Choose CSV File",None,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_OK, gtk.RESPONSE_OK,
                 gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

        oLabel = gtk.Label()
        oLabel.set_markup("<b>Select CSV File ...</b>")
        oLabel.set_alignment(0.0,0.5)
        self.oDlg.vbox.pack_start(oLabel,padding=5)

        self.oFileChooser = SutekhFileButton(self.parent,"Select a CSV File")
        self.oFileChooser.connect("selection-changed",
                                  self._selected_file_changed)
        self.oDlg.vbox.pack_start(self.oFileChooser)

        self.oDlg.vbox.pack_start(gtk.HSeparator(), padding=5)

        oLabel = gtk.Label()
        oLabel.set_markup("<b>Select columns containing ...</b>")
        oLabel.set_alignment(0.0, 0.5)
        self.oDlg.vbox.pack_start(oLabel)

        oNameBox = gtk.HBox()
        oNameBox.pack_start(gtk.Label("Card name:"))
        self.oCardNameCombo = self._create_column_selector()
        oNameBox.pack_start(self.oCardNameCombo)
        self.oDlg.vbox.pack_start(oNameBox)

        oCountBox = gtk.HBox()
        oCountBox.pack_start(gtk.Label("Card count:"))
        self.oCountCombo = self._create_column_selector()
        oCountBox.pack_start(self.oCountCombo)
        self.oDlg.vbox.pack_start(oCountBox)

        oExpansionBox = gtk.HBox()
        oExpansionBox.pack_start(gtk.Label("Expansion name (optional):"))
        self.oExpansionCombo = self._create_column_selector()
        oExpansionBox.pack_start(self.oExpansionCombo)
        self.oDlg.vbox.pack_start(oExpansionBox)

        self._clear_column_selectors()

        self.oDlg.vbox.pack_start(gtk.HSeparator(),padding=5)

        oLabel = gtk.Label()
        oLabel.set_markup("<b>Import as ...</b>")
        oLabel.set_alignment(0.0,0.5)
        self.oDlg.vbox.pack_start(oLabel)

        oIter = self._dCSVImportDestinations.iteritems()
        for sName, (iType, cCardSet) in oIter:
            self._oFirstBut = gtk.RadioButton(None,sName,False)
            self._oFirstBut.set_active(True)
            self.oDlg.vbox.pack_start(self._oFirstBut)
            break
        for sName, iType in oIter:
            oBut = gtk.RadioButton(self._oFirstBut,sName)
            self.oDlg.vbox.pack_start(oBut)

        oCardSetNameBox = gtk.HBox()
        oCardSetNameBox.pack_start(gtk.Label("Card Set Name:"))
        self.oSetNameEntry = gtk.Entry()
        oCardSetNameBox.pack_start(self.oSetNameEntry)
        self.oDlg.vbox.pack_start(oCardSetNameBox)

        self.oDlg.connect("response", self.handle_response)
        self.oDlg.set_size_request(400,400)
        self.oDlg.show_all()

        return self.oDlg

    def _selected_file_changed(self, oFileChooser):
        sFile = oFileChooser.get_filename()
        try:
            fIn = file(sFile,"rb")
        except StandardError, e:
            self._clear_column_selectors()
            return

        try:
            sLine1 = fIn.next()
            sLine2 = fIn.next()
        except StandardError, e:
            self._clear_column_selectors()
            return
        finally:
            fIn.close()

        try:
            oCsv = csv.reader([sLine1,sLine2])
            aRow = oCsv.next()
            sSample = sLine1 + "\n" + sLine2
            oSniff = csv.Sniffer()
            bHasHeader = oSniff.has_header(sSample)
        except (StandardError, csv.Error), e:
            self._clear_column_selectors()
            return

        if bHasHeader:
            aColumns = [(-1,'-')] + list(enumerate(aRow))
        else:
            aColumns = [(-1,'-')] + [(i,str(i)) for i in range(len(aRow))]

        self.oDlg.set_response_sensitive(gtk.RESPONSE_OK,True)
        self._set_column_selectors(aColumns)

    def _create_column_selector(self):
        oListStore = gtk.ListStore(gobject.TYPE_INT,gobject.TYPE_STRING)
        oComboBox = gtk.ComboBox(oListStore)
        oCell = gtk.CellRendererText()
        oComboBox.pack_start(oCell, True)
        oComboBox.add_attribute(oCell, 'text', 1)
        return oComboBox

    def _clear_column_selectors(self):
        # can't click ok until a valid CSV file is chosen
        self.oDlg.set_response_sensitive(gtk.RESPONSE_OK,False)
        self._set_column_selectors([(-1,'-')])

    def _set_column_selectors(self,aColumns):
        for oCombo in (self.oCardNameCombo, self.oCountCombo,
                       self.oExpansionCombo):
            oListStore = oCombo.get_model()
            oListStore.clear()
            for iRow, sHeading in aColumns:
                oIter = oListStore.append(None)
                oListStore.set(oIter, 0, iRow, 1, sHeading)
            oCombo.set_active_iter(oListStore.get_iter_root())

    def handle_response(self,oWidget,oResponse):
        if oResponse == gtk.RESPONSE_OK:
            for oBut in self._oFirstBut.get_group():
                sTypeName = oBut.get_label()
                if oBut.get_active():
                    iFileType, cCardSet = self._dCSVImportDestinations[sTypeName]
                    break

            aCols = []
            for oCombo in (self.oCardNameCombo, self.oCountCombo,
                           self.oExpansionCombo):
                oIter = oCombo.get_active_iter()
                oModel = oCombo.get_model()
                if oIter is None:
                    aCols.append(None)
                else:
                    iVal = oModel.get_value(oIter,0)
                    if iVal < 0:
                        aCols.append(None)
                    else:
                        aCols.append(iVal)

            iCardNameColumn, iCountColumn, iExpansionColumn = aCols

            if iCardNameColumn is None or iCountColumn is None:
                sMsg = "Importing a CSV file requires valid columns for both the card names and card counts."
                do_complaint_error(sMsg)
                self.oDlg.run()
                return

            # Check ACS/PCS Doesn't Exist
            if cCardSet:
                sCardSetName = self.oSetNameEntry.get_text()
                if not sCardSetName:
                    sMsg = "Please specify a name for the %s." % (sTypeName,)
                    do_complaint_error(sMsg)
                    self.oDlg.run()
                    return
                if cCardSet.selectBy(name=sCardSetName).count() != 0:
                    sMsg = "%s '%s' already exists." % (sTypeName, sCardSetName)
                    do_complaint_error(sMsg)
                    self.oDlg.destroy()
                    return
            else:
                sCardSetName = None

            oParser = CSVParser(iCardNameColumn, iCountColumn,
                                iExpansionColumn, bHasHeader=True,
                                iFileType=iFileType)

            sFile = self.oFileChooser.get_filename()

            try:
                fIn = file(sFile,"rb")
            except:
                do_complaint_error("Could not open file '%s'." % sFile)
                self.oDlg.destroy()
                return

            try:
                oParser.parse(fIn, sCardSetName, oCardLookup=self.cardlookup)
            except LookupFailed, e:
                self.oDlg.destroy()
                return
            finally:
                fIn.close()

            if cCardSet is AbstractCardSet:
                self.open_acs(sCardSetName)
            elif cCardSet is PhysicalCardSet:
                self.open_pcs(sCardSetName)
            else:
                self.view.reload_keep_expanded()

        self.oDlg.destroy()

# pylint: disable-msg=C0103
# accept plugin name
plugin = CSVImporter