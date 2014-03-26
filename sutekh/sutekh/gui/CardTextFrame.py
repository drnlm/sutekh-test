# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# The Card Text Frame
# Copyright 2005, 2006, 2007 Simon Cross <hodgestar@gmail.com>
# Copyright 2006, 2007 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Frame to hold the CardTextView."""

import gtk
from sutekh.gui.AutoScrolledWindow import AutoScrolledWindow
from sutekh.gui.CardTextView import CardTextView
from sutekh.gui.BasicFrame import BasicFrame
from sutekh.gui.MessageBus import MessageBus, CARD_TEXT_MSG


class CardTextFrame(BasicFrame):
    """Frame which holds the CardTextView.

       Provides basic frame actions (drag-n-drop, focus behaviour), and
       sets names and such correctly for the TextView.
       """
    # pylint: disable-msg=R0904
    # gtk.Widget, so lots of public methods
    def __init__(self, oMainWindow, oIconManager):
        super(CardTextFrame, self).__init__(oMainWindow)
        self._oView = CardTextView(oMainWindow, oIconManager)
        self.add_parts()
        self.set_name('card text')

    type = property(fget=lambda self: "Card Text", doc="Frame Type")

    def add_parts(self):
        """Add TextView + title widgets to the Frame."""
        oBox = gtk.VBox(False, 2)
        self.set_title("Card Text")

        oBox.pack_start(self._oTitle, False, False)

        oBox.pack_start(AutoScrolledWindow(self._oView), True, True)

        self.set_drop_handler(self._oView)

        self.add(oBox)
        self.show_all()

    def frame_setup(self):
        """Subscribe to the set_card_text signal"""
        self._oView.clear_text()
        MessageBus.subscribe(CARD_TEXT_MSG, 'set_card_text',
                             self.set_card_text)
        super(CardTextFrame, self).frame_setup()

    def cleanup(self):
        """Cleanup the listeners"""
        MessageBus.unsubscribe(CARD_TEXT_MSG, 'set_card_text',
                               self.set_card_text)
        super(CardTextFrame, self).cleanup()

    def set_card_text(self, oCard):
        """Hand off card text update to the view"""
        if oCard:
            # Skip doing anything if None
            self._oView.set_card_text(oCard)

    def update_to_new_db(self):
        """Ensure we update cached results so DB changes don't cause odd
           results"""
        self._oView.update_to_new_db()

    def get_menu_name(self):
        """Get the menu key"""
        return "Card Text"
