# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Simon Cross <hodgestar@gmail.com>,
# Copyright 2006 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Display a running total of the cards in a card set"""

from sutekh.core.Objects import PhysicalCardSet, IAbstractCard
from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.gui.generic.baseplugins.BaseCountCSCards import BaseCountCSCards
from sutekh.SutekhUtility import is_crypt_card


TOTAL, CRYPT, LIB = 'tot', 'crypt', 'lib'


class CountCardSetCards(SutekhPlugin, BaseCountCSCards):
    """Listen to changes on the card list views, and display a toolbar
       containing a label with a running count of the cards in the card
       set, the library cards and the crypt cards
       """
    dTableVersions = {PhysicalCardSet: (5, 6)}
    aModelsSupported = (PhysicalCardSet,)

    TOT_FORMAT = 'Tot: <b>%(tot)d</b> L: <b>%(lib)d</b> C: <b>%(crypt)d</b>'
    TOT_TOOLTIP = 'Total Cards: <b>%(tot)d</b> (Library: <b>%(lib)d</b>' \
            ' Crypt: <b>%(crypt)d</b>)'

    # pylint: disable-msg=W0142
    # **magic OK here
    def __init__(self, *args, **kwargs):
        super(CountCardSetCards, self).__init__(*args, **kwargs)

        self._iTot = 0
        self._iCrypt = 0
        self._iLibrary = 0
    # pylint: enable-msg=W0142

    def _get_count_info(self):
        """Update the label"""
        # Timing issues mean that this can be called before text label has
        # been properly realised, so we need this guard case
        return {TOTAL: self._iTot, CRYPT: self._iCrypt,
                 LIB: self._iLibrary}

    def _do_load(self, aCards):
        """Listen on load events & update counts"""
        # We cache type  lookups to save time
        # The cache is short-lived to avoid needing to deal with
        # flushing the cache on database changes.
        dCache = {}
        self._iCrypt = 0
        self._iLibrary = 0
        self._iTot = len(aCards)
        for oCard in aCards:
            bCrypt = dCache.get(oCard.id, None)
            if bCrypt is None:
                oAbsCard = IAbstractCard(oCard)
                bCrypt = is_crypt_card(oAbsCard)
                dCache[oCard.id] = bCrypt
            if bCrypt:
                self._iCrypt += 1
            else:
                self._iLibrary += 1

    def _do_alter_card_count(self, oCard, iChg):
        """respond to alter_card_count events"""
        self._iTot += iChg
        oAbsCard = IAbstractCard(oCard)
        if is_crypt_card(oAbsCard):
            self._iCrypt += iChg
        else:
            self._iLibrary += iChg

    def _do_add_new_card(self, oCard, iCnt):
        """response to add_new_card events"""
        self._iTot += iCnt
        oAbsCard = IAbstractCard(oCard)
        if is_crypt_card(oAbsCard):
            self._iCrypt += iCnt
        else:
            self._iLibrary += iCnt


plugin = CountCardSetCards
