# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Adds a frame which will display card images from ARDB in the GUI"""

import gtk
import os
import tempfile
import logging
from sqlobject import SQLObjectNotFound
from sutekh.core.Objects import IExpansion
from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.gui.generic.SutekhDialog import SutekhDialog, do_complaint_error
from sutekh.SutekhUtility import prefs_dir, ensure_dir_exists
from sutekh.gui.generic.FileOrUrlWidget import FileOrDirOrUrlWidget
from sutekh.gui.generic.SutekhFileWidget import add_filter
from sutekh.gui.generic.baseplugins.BaseImages import (BaseImageFrame,
        BaseImagePlugin, check_file, unaccent)


class CardImageFrame(BaseImageFrame):
    # pylint: disable-msg=R0904, R0902
    # R0904 - can't not trigger these warning with pygtk
    # R0902 - we need to keep quite a lot of internal state
    """Frame which displays the image.

       We wrap a gtk.Image in an EventBox (for focus & DnD events)
       and a Viewport (for scrolling)
       """

    sMenuFlag = 'Card Image Frame'

    def __init__(self, oImagePlugin):
        super(CardImageFrame, self).__init__(oImagePlugin)
        if self._sPrefsPath is None:
            self._sPrefsPath = os.path.join(prefs_dir('Sutekh'), 'cardimages')
            self._oImagePlugin.set_config_item('card image path',
                    self._sPrefsPath)

    def _have_expansions(self, sTestPath=''):
        """Test if directory contains expansion/image structure used by ARDB"""
        if sTestPath == '':
            sTestFile = os.path.join(self._sPrefsPath, 'bh', 'acrobatics.jpg')
        else:
            sTestFile = os.path.join(sTestPath, 'bh', 'acrobatics.jpg')
        return check_file(sTestFile)

    def _convert_expansion(self, sExpansionName):
        """Convert the Full Expansion name into the abbreviation needed."""
        if sExpansionName == '' or not self._bShowExpansions:
            return ''
        # pylint: disable-msg=E1101
        # pylint doesn't pick up IExpansion methods correctly
        try:
            oExpansion = IExpansion(sExpansionName)
        except SQLObjectNotFound:
            # This can happen because we cache the expansion name and
            # a new database import may cause that to vanish.
            # We return just return a blank path segment, as the safest choice
            logging.warn('Expansion %s no longer found in the database',
                    sExpansionName)
            return ''
        # special case Anarchs and alastors due to promo hack shortname
        if oExpansion.name == 'Anarchs and Alastors Storyline':
            sExpName = oExpansion.name.lower()
        else:
            sExpName = oExpansion.shortname.lower()
        # Normalise for storyline cards
        sExpName = sExpName.replace(' ', '_').replace("'", '')
        return sExpName

    def _make_card_url(self):
        """Return a url pointing to the vtes.pl scan of the image"""
        sCurExpansionPath = self._convert_expansion(self._sCurExpansion)
        sFilename = self._norm_cardname()
        if sCurExpansionPath == '' or sFilename == '':
            # Error path, we don't know where to search for the image
            return ''
        # Remap paths to point to the vtes.pl equivilents
        if sCurExpansionPath == 'nergal_storyline':
            sCurExpansionPath = 'isl'
        elif sCurExpansionPath == 'anarchs_and_alastors_storyline':
            sCurExpansionPath = 'aa'
        elif sCurExpansionPath == 'edens_legacy_storyline':
            sCurExpansionPath = 'el'
        elif sCurExpansionPath == 'cultist_storyline':
            sCurExpansionPath = 'csl'
        elif sCurExpansionPath == 'white_wolf_2003_demo':
            sCurExpansionPath = 'dd'
        elif sCurExpansionPath == 'third':
            sCurExpansionPath = '3e'
        return 'http://nekhomanta.h2.pl/pics/games/vtes/%s/%s' % (
                sCurExpansionPath, sFilename)

    def _norm_cardname(self):
        """Normalise the card name"""
        sFilename = unaccent(self._sCardName)
        if sFilename.startswith('the '):
            sFilename = sFilename[4:] + 'the'
        elif sFilename.startswith('an '):
            sFilename = sFilename[3:] + 'an'
        sFilename = sFilename.replace('(advanced)', 'adv')
        # Should probably do this via translate
        for sChar in (" ", ".", ",", "'", "(", ")", "-", ":", "!", '"', "/"):
            sFilename = sFilename.replace(sChar, '')
        sFilename = sFilename + '.jpg'
        return sFilename

    def check_images(self, sTestPath=''):
        """Check if dir contains images in the right structure"""
        self._bShowExpansions = self._have_expansions(sTestPath)
        if self._bShowExpansions:
            return True
        if sTestPath == '':
            sTestFile = os.path.join(self._sPrefsPath, 'acrobatics.jpg')
        else:
            sTestFile = os.path.join(sTestPath, 'acrobatics.jpg')
        return check_file(sTestFile)


class ImageConfigDialog(SutekhDialog):
    # pylint: disable-msg=R0904
    # R0904 - gtk Widget, so has many public methods
    """Dialog for configuring the Image plugin."""

    sDefaultUrl = 'http://csillagmag.hu/upload/pictures.zip'

    def __init__(self, oImagePlugin, bFirstTime=False, bDownloadUpgrade=False):
        super(ImageConfigDialog, self).__init__('Configure Card Images Plugin',
                oImagePlugin.parent,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL,
                    gtk.RESPONSE_CANCEL))
        oDescLabel = gtk.Label()
        if not bFirstTime and not bDownloadUpgrade:
            oDescLabel.set_markup('<b>Choose how to configure the cardimages '
                    'plugin</b>')
        elif bDownloadUpgrade:
            oDescLabel.set_markup('<b>Choose how to configure the cardimages '
                    'plugin</b>\nThe card images plugin can now download '
                    'missing images from vtes.pl.\nDo you wish to enable '
                    'this (you will not be prompted again)?')
        else:
            oDescLabel.set_markup('<b>Choose how to configure the cardimages '
                    'plugin</b>\nChoose cancel to skip configuring the '
                    'images plugin\nYou will not be prompted again')
        sDefaultDir = oImagePlugin.get_config_item('card image path')
        self.oChoice = FileOrDirOrUrlWidget(oImagePlugin.parent,
                "Choose location for "
                "images file", "Choose image directory", sDefaultDir,
                {'csillagbolcselet.hu': self.sDefaultUrl})
        add_filter(self.oChoice, 'Zip Files', ['*.zip', '*.ZIP'])
        # pylint: disable-msg=E1101
        # pylint doesn't pick up vbox methods correctly
        self.vbox.pack_start(oDescLabel, False, False)
        if not bFirstTime:
            # Set to the null choice
            self.oChoice.select_by_name('Select directory ...')
        if not bDownloadUpgrade:
            # Don't prompt for the file if we just want to ask about
            # downloading images
            self.vbox.pack_start(self.oChoice, False, False)
        self.oDownload = gtk.CheckButton(
                'Download missing images from vtes.pl?')
        self.oDownload.set_active(False)
        self.vbox.pack_start(self.oDownload, False, False)
        self.set_size_request(400, 200)

        self.show_all()

    def get_data(self):
        """Get the results of the users choice."""
        sFile, _bUrl, bDir = self.oChoice.get_file_or_dir_or_url()
        bDownload = self.oDownload.get_active()
        if bDir:
            # Just return the name the user chose
            return sFile, True, bDownload
        if sFile:
            oOutFile = tempfile.TemporaryFile()
            self.oChoice.get_binary_data(oOutFile)
            return oOutFile, False, bDownload
        return None, None, bDownload


class CardImagePlugin(SutekhPlugin, BaseImagePlugin):
    """Plugin providing access to CardImageFrame."""
    dTableVersions = {}
    aModelsSupported = ("MainWindow",)

    cCardFrame = CardImageFrame

    def setup(self):
        """Prompt the user to download/setup images the first time"""
        sPrefsPath = self.get_config_item('card image path')
        if not os.path.exists(sPrefsPath):
            # Looks like the first time
            oDialog = ImageConfigDialog(self, True, False)
            self.handle_response(oDialog)
            # Path may have been changed, so we need to requery config file
            sPrefsPath = self.get_config_item('card image path')
            # Don't get called next time
            ensure_dir_exists(sPrefsPath)
        else:
            oDownloadImages = self.get_config_item('download images')
            if oDownloadImages is None:
                # Doesn't look like we've asked this question
                oDialog = ImageConfigDialog(self, False, True)
                # Default to false
                self.set_config_item('download images', False)
                self.handle_response(oDialog)

    def config_activate(self, _oMenuWidget):
        """Configure the plugin dialog."""
        oDialog = ImageConfigDialog(self, False, False)
        self.handle_response(oDialog)

    def handle_response(self, oDialog):
        """Handle the response from the config dialog"""
        iResponse = oDialog.run()
        bActivateMenu = False
        if iResponse == gtk.RESPONSE_OK:
            oFile, bDir, bDownload = oDialog.get_data()
            if bDir:
                # New directory
                if self._accept_path(oFile):
                    # Update preferences
                    self.image_frame.update_config_path(oFile)
                    bActivateMenu = True
            elif oFile:
                if self._unzip_file(oFile):
                    bActivateMenu = True
                else:
                    do_complaint_error('Unable to successfully unzip data')
                oFile.close()  # clean up temp file
            else:
                # Unable to get data
                do_complaint_error('Unable to configure card images plugin')
            # Update download option
            self.set_config_item('download images', bDownload)
        if bActivateMenu:
            # Update the menu display if needed
            if not self.parent.is_open_by_menu_name(self._sMenuFlag):
                # Pane is not open, so try to enable menu
                self.add_image_frame_active(True)
        # get rid of the dialog
        oDialog.destroy()


plugin = CardImagePlugin
