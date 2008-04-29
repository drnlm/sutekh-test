# IconManager.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Manage the icons from the WW site"""

import gtk
import gobject
import os
from logging import Logger
from urllib2 import urlopen, HTTPError
from sutekh.SutekhUtility import prefs_dir, ensure_dir_exists
from sutekh.core.SutekhObjects import Clan, Creed, CardType, DisciplinePair, \
        Virtue
from sutekh.gui.ProgressDialog import ProgressDialog, SutekhCountLogHandler

# Utilty functions - convert object to a filename
def _get_clan_filename(oClan):
    """Get the icon filename for the clan"""
    if oClan.shortname[0] == '!':
        sFileName = 'IconClan%sA.gif' % oClan.shortname[1:4].capitalize()
    elif oClan.shortname == 'Tz':
        # Special case
        sFileName = 'IconClanTzi.gif'
    else:
        sFileName = 'IconClan%s.gif' % oClan.shortname[:3].capitalize()
    return sFileName

def _get_card_type_filename(oType):
    """Get the filename for the card type"""
    if oType.name == 'Conviction':
        sFileName = 'IconConviction.gif'
    elif oType.name == 'Equipment':
        sFileName = 'IconTypeEquip.gif'
    elif oType.name == 'Political Action':
        sFileName = 'IconTypePolitical.gif'
    elif oType.name == 'Action Modifier':
        sFileName = 'IconTypeModifier.gif'
    elif oType.name in ['Master', 'Vampire', 'Imbued']:
        # These types have no icon
        sFileName = None
    else:
        sFileName = 'IconType%s.gif' % oType.name.capitalize()
    return sFileName

def _get_creed_filename(oCreed):
    """Get the filename for the creed"""
    sFileName = 'IconCreed%s.gif' % oCreed.shortname[:3].capitalize()
    return sFileName

def _get_discipline_filename(oDiscipline):
    """Get the filename for the discipline."""
    if oDiscipline.level == 'inferior':
        sFileName = 'IconDis%s.gif' % oDiscipline.discipline.name.capitalize()
    elif oDiscipline.discipline.fullname == 'Flight':
        # Flight is always Superior
        sFileName = 'IconFlight.gif'
    else:
        sFileName = 'IconDis%s2.gif' % oDiscipline.discipline.name.capitalize()
    return sFileName

def _get_virtue_filename(oVirtue):
    """Get the filename for the virtue"""
    sFileName = 'IconVirtue%s.gif' % oVirtue.name.capitalize()
    return sFileName

# Crop the transparent border from the image
def _crop_alpha(oPixbuf):
    """Crop the transparent padding from a pixbuf.

       Needed to reduce scaling issues with the clan icons.
       """
    def _check_margins(iVal, iMax, iMin):
        """Check if the margins need to be updated"""
        if iVal < iMin:
            iMin = iVal
        if iVal > iMax:
            iMax = iVal
        return iMax, iMin
    # We don't use get_pixels_array, since numeric support is optional
    # These are gif's so the transparency is either 255 - opaque or 0 -
    # transparent. We want the bounding box of the non-transparent pixels
    iRowLength = oPixbuf.get_width()*4
    iMaxX, iMaxY = -1, -1
    iMinX, iMinY = 1000, 1000
    iXPos, iYPos = 0, 0
    for cPixel in oPixbuf.get_pixels():
        if iXPos % 4 == 3:
            # Data is ordered RGBA, so this is the alpha channel
            if ord(cPixel) == 255:
                # Is opaque, so update margins
                iMaxX, iMinX = _check_margins(iXPos / 4, iMaxX, iMinX)
                iMaxY, iMinY = _check_margins(iYPos, iMaxY, iMinY)
        iXPos += 1
        if iXPos == iRowLength:
            # End of a line
            iYPos += 1
            iXPos = 0
    return oPixbuf.subpixbuf(iMinX + 1, iMinY + 1, iMaxX - iMinX,
            iMaxY - iMinY)

class IconManager(object):
    """Manager for the VTES Icons.

       Given the text and the tag name, look up the suitable matching icon
       for it.  Return none if no suitable icon is found.
       Also provide an option to download the icons form the white wolf
       site.
       """

    sBaseUrl = "http://www.white-wolf.com/vtes/images/"
    def __init__(self, oConfig):
        # TODO: Get icon path from the config file if set
        self._sPrefsDir = os.path.join(prefs_dir('Sutekh'), 'icons')
        self._dIconCache = {}

    def _get_icon(self, sFileName, iSize=12):
        """get the cached icon, or load it if needed."""
        if not sFileName:
            return None
        if self._dIconCache.has_key(sFileName):
            return self._dIconCache[sFileName]
        try:
            sFullFilename = os.path.join(self._sPrefsDir, sFileName)
            oPixbuf = gtk.gdk.pixbuf_new_from_file(sFullFilename)
            # Crop the transparent border
            oPixbuf = _crop_alpha(oPixbuf)
            # Scale, but preserve aspect ratio
            iHeight = iSize
            iWidth = iSize
            iPixHeight = oPixbuf.get_height()
            iPixWidth = oPixbuf.get_width()
            fAspect = iPixHeight / float(iPixWidth)
            if iPixWidth > iPixHeight:
                iHeight = int(fAspect * iSize)
            elif iPixHeight > iPixWidth:
                iWidth = int(iSize / fAspect)
            oPixbuf = oPixbuf.scale_simple(iWidth, iHeight,
                    gtk.gdk.INTERP_TILES)
        except gobject.GError:
            oPixbuf = None
        self._dIconCache[sFileName] = oPixbuf
        return oPixbuf

    def _get_clan_icons(self, aValues):
        """Get the icons for the clans"""
        dIcons = {}
        for oClan in aValues:
            sFileName = _get_clan_filename(oClan)
            dIcons[oClan.name] = self._get_icon(sFileName)
        return dIcons

    def _get_card_type_icons(self, aValues):
        """Get the icons for the card types"""
        dIcons = {}
        for oType in aValues:
            sFileName = _get_card_type_filename(oType)
            dIcons[oType.name] = self._get_icon(sFileName)
        return dIcons

    def _get_creed_icons(self, aValues):
        """Get the icons for the creeds."""
        dIcons = {}
        for oCreed in aValues:
            sFileName = _get_creed_filename(oCreed)
            dIcons[oCreed.name] = self._get_icon(sFileName)
        return dIcons

    def _get_discipline_icons(self, aValues):
        """Get the icons for the disciplines."""
        dIcons = {}
        for oDiscipline in aValues:
            sFileName = _get_discipline_filename(oDiscipline)
            if oDiscipline.level == 'superior':
                oIcon = self._get_icon(sFileName, 14)
            else:
                oIcon = self._get_icon(sFileName)
            dIcons[oDiscipline.discipline.name] = oIcon
        return dIcons

    def _get_virtue_icons(self, aValues):
        """Get the icons for the Virtues."""
        dIcons = {}
        for oVirtue in aValues:
            sFileName = _get_virtue_filename(oVirtue)
            dIcons[oVirtue.name] = self._get_icon(sFileName)
        return dIcons

    def get_icon_by_name(self, sName):
        """Lookup an icon that's a card property"""
        if sName == 'burn option':
            sFileName = 'IconBurn.gif'
        elif sName == 'advanced':
            sFileName = 'IconAdv.gif'
        return self._get_icon(sFileName)

    def get_icon_list(self, aValues):
        """Get a list of appropriate icons for the given values"""
        if not aValues:
            return None
        aIcons = None
        oType = type(aValues[0])
        if oType is CardType:
            aIcons = self._get_card_type_icons(aValues)
        elif oType is DisciplinePair:
            aIcons = self._get_discipline_icons(aValues)
        elif oType is Virtue:
            aIcons = self._get_virtue_icons(aValues)
        elif oType is Clan:
            aIcons = self._get_clan_icons(aValues)
        elif oType is Creed:
            aIcons = self._get_creed_icons(aValues)
        return aIcons

    def download_icons(self):
        """Download the icons from the WW site"""
        # TODO: change the names to something more sensible
        def download(sFileName, oLogger):
            """Download the icon and save it in the icons directory"""
            if not sFileName:
                oLogger.info('Processed non-icon')
                return
            sFullFilename = os.path.join(self._sPrefsDir, sFileName)
            sUrl = self.sBaseUrl + sFileName
            try:
                oUrl = urlopen(sUrl)
                # copy url to file
                fOut = file(sFullFilename, 'w')
                fOut.write(oUrl.read())
                fOut.close()
            except HTTPError, oErr:
                print 'Unable to download %s: Error %s' % (sUrl, oErr)
            oLogger.info('Processed %s' % sFileName)
        self._dIconCache = {} # Cache is invalidated by this
        ensure_dir_exists(self._sPrefsDir)
        oLogHandler = SutekhCountLogHandler()
        oProgressDialog = ProgressDialog()
        oProgressDialog.set_description("Downloading icons")
        oLogHandler.set_dialog(oProgressDialog)
        oProgressDialog.show()
        oLogHandler.set_total(Creed.select().count() +
                DisciplinePair.select().count() + Clan.select().count() +
                Virtue.select().count() + CardType.select().count() + 2)
        oLogger = Logger('Download Icons')
        oLogger.addHandler(oLogHandler)
        for oCreed in Creed.select():
            download(_get_creed_filename(oCreed), oLogger)
        for oDiscipline in DisciplinePair.select():
            download(_get_discipline_filename(oDiscipline), oLogger)
        for oClan in Clan.select():
            download(_get_clan_filename(oClan), oLogger)
        for oVirtue in Virtue.select():
            download(_get_virtue_filename(oVirtue), oLogger)
        for oType in CardType.select():
            download(_get_card_type_filename(oType), oLogger)
        # download the special cases
        download('IconBurn.gif', oLogger)
        download('IconAdv.gif', oLogger)
        oProgressDialog.destroy()