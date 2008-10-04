# CellRendererIcons.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Pixbuf Button CellRenderer
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Render a list VTES icons and text in a TreeView"""

import gtk, pango

# pylint: disable-msg=C0103
# We break our usual convention here
# consts for the different display modes we need
SHOW_TEXT_ONLY, SHOW_ICONS_ONLY, SHOW_ICONS_AND_TEXT = range(3)
# pylint: enable-msg=C0103

def _layout_text(oLayout, sText):
    """Helper function to ensure consistency in calling layout"""
    oLayout.set_markup("<i>%s </i>" % sText)
    oLayout.set_alignment(pango.ALIGN_LEFT)


# pylint: disable-msg=R0904
# gtk widget, so we must have a lot of public methods
class CellRendererIcons(gtk.GenericCellRenderer):
    """Render a list of icons and text in a cell in a TreeView.

       Used to render the VTES icons in the CardListViews
       """
    # Pad constants
    iTextPad = 4
    iIconPad = 2

    def __init__(self):
        super(CellRendererIcons, self).__init__()
        self.aData = []
        self.iMode = SHOW_ICONS_AND_TEXT

    def set_data(self, aText, aIcons, iMode=SHOW_ICONS_AND_TEXT):
        """Load the info needed to render the icon"""
        self.aData = []
        if len(aIcons) != len(aText):
            # Can't handle this case
            return False
        self.aData = zip(aText, aIcons)
        self.iMode = iMode

    # pylint: disable-msg=W0613
    # oWidget equired by function signature
    def on_get_size(self, oWidget, oCellArea):
        """Handle get_size requests"""
        if not self.aData:
            return 0, 0, 0, 0
        iCellWidth = 0
        iCellHeight = 0
        oLayout = oWidget.create_pango_layout("")
        for sText, oIcon in self.aData:
            # Get icon dimensions
            if oIcon and self.iMode != SHOW_TEXT_ONLY:
                iCellWidth += oIcon.get_width() + self.iIconPad
                if oIcon.get_height() > iCellHeight:
                    iCellHeight = oIcon.get_height()
            # Get text dimensions
            if sText and (self.iMode != SHOW_ICONS_ONLY or oIcon is None):
                # always fallback to text if oIcon is None
                _layout_text(oLayout, sText)
                # get layout dimensions
                iWidth, iHeight = oLayout.get_pixel_size()
                # add padding to width
                if iHeight > iCellHeight:
                    iCellHeight = iHeight
                iCellWidth += iWidth + self.iTextPad
        fCalcWidth  = self.get_property("xpad") * 2 + iCellWidth
        fCalcHeight = self.get_property("ypad") * 2 + iCellHeight
        iXOffset = 0
        iYOffset = 0
        if oCellArea is not None and iCellWidth > 0 and iCellHeight > 0:
            iXOffset = int(self.get_property("xalign") * (oCellArea.width - \
                fCalcWidth -  self.get_property("xpad")))
            iYOffset = int(self.get_property("yalign") * (oCellArea.height - \
                fCalcHeight -  self.get_property("ypad")))
        # gtk want's ints here
        return iXOffset, iYOffset, int(fCalcWidth), int(fCalcHeight)

    # pylint: disable-msg=W0613, R0913
    # R0913 - number of parameters needed by function signature
    # W0613 - iFlags required by function signature
    def on_render(self, oWindow, oWidget, oBackgroundArea,
            oCellArea, oExposeArea, iFlags):
        """Render the icons & text for the tree view"""
        oLayout = oWidget.create_pango_layout("")
        oPixRect = gtk.gdk.Rectangle()
        oPixRect.x, oPixRect.y, oPixRect.width, oPixRect.height = \
            self.on_get_size(oWidget, oCellArea)
        # We want to always start at the left edge of the Cell, so this is
        # correct
        oPixRect.x = oCellArea.x
        oPixRect.y += oCellArea.y
        # xpad, ypad are floats, but gtk.gdk.Rectangle needs int's
        oPixRect.width  -= int(2 * self.get_property("xpad"))
        oPixRect.height -= int(2 * self.get_property("ypad"))
        oDrawRect = gtk.gdk.Rectangle()
        oDrawRect.x = int(oPixRect.x)
        oDrawRect.y = int(oPixRect.y)
        oDrawRect.width = 0
        oDrawRect.height = 0
        for sText, oIcon in self.aData:
            if oIcon and self.iMode != SHOW_TEXT_ONLY:
                # Render icon
                oDrawRect.width = oIcon.get_width()
                oDrawRect.height = oIcon.get_height()
                oIconDrawRect = oCellArea.intersect(oDrawRect)
                oIconDrawRect = oExposeArea.intersect(oIconDrawRect)
                oWindow.draw_pixbuf(oWidget.style.black_gc, oIcon,
                        oIconDrawRect.x - oDrawRect.x,
                        oIconDrawRect.y - oDrawRect.y, oIconDrawRect.x,
                        oIconDrawRect.y, -1, oIconDrawRect.height,
                        gtk.gdk.RGB_DITHER_NONE, 0, 0)
                oDrawRect.x += oIcon.get_width() + self.iIconPad
            if sText and (self.iMode != SHOW_ICONS_ONLY or oIcon is None):
                # Render text
                _layout_text(oLayout, sText)
                oDrawRect.width, oDrawRect.height = oLayout.get_pixel_size()
                oWindow.draw_layout(oWidget.style.black_gc, oDrawRect.x,
                        oDrawRect.y, oLayout)
                oDrawRect.x += oDrawRect.width + self.iTextPad
        return None
