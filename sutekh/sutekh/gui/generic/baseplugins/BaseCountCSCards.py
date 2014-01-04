# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Simon Cross <hodgestar@gmail.com>,
# Copyright 2006 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Display a running total of the cards in a card set"""

import gtk
from ..BasePluginManager import BasePlugin
from ..MessageBus import MessageBus


class BaseCountCSCards(BasePlugin):
    """Listen to changes on the card list views, and display a toolbar
       containing a label with a running count of the cards in the card
       set, the library cards and the crypt cards
       """
    TOT_FORMAT = ''
    TOT_TOOLTIP = ''

    # pylint: disable-msg=W0142
    # **magic OK here
    def __init__(self, *args, **kwargs):
        super(BaseCountCSCards, self).__init__(*args, **kwargs)

        self._oTextLabel = None

        # We only add listeners to windows we're going to display the toolbar
        # on
        if self.check_versions() and self.check_model_type():
            MessageBus.subscribe(self.model, 'add_new_card', self.add_new_card)
            MessageBus.subscribe(self.model, 'alter_card_count',
                    self.alter_card_count)
            MessageBus.subscribe(self.model, 'load', self.load)
    # pylint: enable-msg=W0142

    def cleanup(self):
        """Remove the listener"""
        if self.check_versions() and self.check_model_type():
            MessageBus.unsubscribe(self.model, 'add_new_card',
                    self.add_new_card)
            MessageBus.unsubscribe(self.model, 'alter_card_count',
                    self.alter_card_count)
            MessageBus.unsubscribe(self.model, 'load', self.load)
        super(BaseCountCSCards, self).cleanup()

    def get_toolbar_widget(self):
        """Overrides method from base class."""
        if not self.check_versions() or not self.check_model_type():
            return None

        dInfo = self._get_count_info()

        self._oTextLabel = gtk.Label(self.TOT_FORMAT % dInfo)
        self._oTextLabel.set_tooltip_markup(self.TOT_TOOLTIP % dInfo)
        self._oTextLabel.show()
        return self._oTextLabel

    def update_numbers(self):
        """Update the label"""
        # Timing issues mean that this can be called before text label has
        # been properly realised, so we need this guard case
        if self._oTextLabel:
            dInfo = self._get_count_info()
            self._oTextLabel.set_markup(self.TOT_FORMAT % dInfo)
            self._oTextLabel.set_tooltip_markup(self.TOT_TOOLTIP % dInfo)

    def _get_count_info(self):
        """Return a dict of the card count info"""
        raise NotImplementedError("implemment _get_count_info")

    def _do_load(self, aCards):
        """Heavy lifiting of load signal"""
        raise NotImplementedError("implemment _do_load")

    def _do_alter_card_count(self, oCard, iChg):
        """Heavy lifiting of add_new_card signal"""
        raise NotImplementedError("implemment _do_add_new_card")

    def _do_add_new_card(self, oCard, iCnt):
        """Heavy lifiting of add_new_card signal"""
        raise NotImplementedError("implemment _do_add_new_card")

    def load(self, aCards):
        """Listen on load events & update counts"""
        self._do_load(aCards)
        self.update_numbers()

    def alter_card_count(self, oCard, iChg):
        """respond to alter_card_count events"""
        self._do_alter_card_count(oCard, iChg)
        self.update_numbers()

    def add_new_card(self, oCard, iCnt):
        """response to add_new_card events"""
        self._do_add_new_card(oCard, iCnt)
        self.update_numbers()
