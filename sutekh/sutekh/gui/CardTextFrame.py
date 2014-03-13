# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# The Card Text Frame
# Copyright 2005, 2006, 2007 Simon Cross <hodgestar@gmail.com>
# Copyright 2006, 2007 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Frame to hold the CardTextView."""

from sutekh.base.gui.ScrolledFrame import BaseCardTextFrame
from sutekh.gui.CardTextView import CardTextView
from sutekh.base.gui.MessageBus import MessageBus, CARD_TEXT_MSG


class CardTextFrame(BaseCardTextFrame):
    """Frame which holds the CardTextView.

       Provides basic frame actions (drag-n-drop, focus behaviour), and
       sets names and such correctly for the TextView.
       """

    # pylint: disable-msg=R0904
    # gtk.Widget, so lots of public methods
    def __init__(self, oMainWindow, oIconManager):
        oView = CardTextView(oMainWindow, oIconManager)
        super(CardTextFrame, self).__init__(oView, oMainWindow)
