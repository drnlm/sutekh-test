# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Simon Cross <hodgestar@gmail.com>,
# Copyright 2006 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Provide count card options for the WW card list"""

from sutekh.core.Objects import PhysicalCard, IAbstractCard
from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.SutekhUtility import is_crypt_card
from sutekh.gui.generic.baseplugins.BaseCountCardListCards import BaseCountCardListCards
from sutekh.gui.plugins.CountCardSetCards import TOT_FORMAT, TOT_TOOLTIP, \
        TOTAL, CRYPT, LIB

SORT_COLUMN_OFFSET = 300  # ensure we don't clash with other extra columns


class CountWWListCards(SutekhPlugin, BaseCountCardListCards):
    """Listen to changes on the card list views, and display a toolbar
       containing a label with a running count of the cards in the card
       set, the library cards and the crypt cards
       """
    dTableVersions = {PhysicalCard: (2,)}
    aModelsSupported = (PhysicalCard,)

    FORMAT = TOT_FORMAT
    TOOLTIP = TOT_TOOLTIP

    # pylint: disable-msg=W0142
    # **magic OK here
    def __init__(self, *args, **kwargs):
        super(CountWWListCards, self).__init__(*args, **kwargs)

        self._dCardTotals = {TOTAL: 0, CRYPT: 0, LIB: 0}
        self._dExpTotals = {TOTAL: 0, CRYPT: 0, LIB: 0}

    def _get_card_count_info(self):
        return self._dCardTotals

    def _get_exp_count_info(self):
        return self._dExpTotals

    def _do_load(self, aCards):
        """Listen on load events & update counts"""
        # The logic is a bit complicated, but it's intended that
        # filtering the WW cardlist on a card set will give sensible
        # results.
        self._dAbsCounts = {}
        self._dExpCounts = {}
        self._dCardTotals = {TOTAL: 0, CRYPT: 0, LIB: 0}
        self._dExpTotals = {TOTAL: 0, CRYPT: 0, LIB: 0}
        for oCard in aCards:
            oAbsCard = IAbstractCard(oCard)
            if oAbsCard not in self._dAbsCounts:
                self._dAbsCounts[oAbsCard] = 1
                iAbsCount = 1
            else:
                iAbsCount = 0
            if oCard.expansionID:
                # We don't count expansion ifno for cards with no expansion set
                iExpCount = 1
                if oAbsCard not in self._dExpCounts:
                    # First time we've seen this card
                    self._dExpCounts[oAbsCard] = 1
                else:
                    # Has an expansion, and by the nature of the list, this is
                    # a new expansion for the card we haven't seen before
                    self._dExpCounts[oAbsCard] += 1
            else:
                iExpCount = 0
            if is_crypt_card(oAbsCard):
                self._dExpTotals[CRYPT] += iExpCount
                self._dCardTotals[CRYPT] += iAbsCount
            else:
                self._dExpTotals[LIB] += iExpCount
                self._dCardTotals[LIB] += iAbsCount
            self._dCardTotals[TOTAL] += iAbsCount
            self._dExpTotals[TOTAL] += iExpCount


plugin = CountWWListCards
