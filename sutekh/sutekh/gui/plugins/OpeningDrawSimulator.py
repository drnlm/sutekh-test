# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Dialog to display deck analysis software
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>,
# GPL - see COPYING for details
"""Simulate the opening hand draw."""

import gtk
from copy import copy
from sutekh.core.Objects import PhysicalCardSet
from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.gui.generic.SutekhDialog import do_complaint_error
from sutekh.gui.generic.baseplugins.BaseOpeningDraw import (BaseOpeningDraw,
        get_cards_filter, get_probs, check_card, fill_string, format_dict,
        hypergeometric_mean, setup_grouped_view, setup_ungrouped_view,
        draw_x_cards)
from sutekh.core.Filters import (CryptCardFilter, MultiCardTypeFilter,
        CardTypeFilter, CardFunctionFilter, FilterNot)


class OpeningHandSimulator(SutekhPlugin, BaseOpeningDraw):
    """Simulate opening hands."""
    dTableVersions = {PhysicalCardSet: (4, 5, 6)}
    aModelsSupported = (PhysicalCardSet,)


    # pylint: disable-msg=W0142
    # **magic OK here
    def __init__(self, *args, **kwargs):
        super(OpeningHandSimulator, self).__init__(*args, **kwargs)
        self.aLibrary = []
        self.aCrypt = []
        self.iMoreLib = 0
        self.iMoreCrypt = 0

    def _get_card_info(self):
        """Create the actual dialog, and populate it"""
        oCryptFilter = CryptCardFilter()

        self.aCrypt = get_cards_filter(self.model, oCryptFilter)
        self.aLibrary = get_cards_filter(self.model, FilterNot(oCryptFilter))

        if len(self.aLibrary) < 7:
            do_complaint_error('Library needs to be at least as large as the'
                    ' opening hand')
            return False

        if len(self.aCrypt) < 4:
            do_complaint_error('Crypt needs to be at least as large as the'
                    ' opening draw')
            return False

        for sType in MultiCardTypeFilter.get_values():
            aList = get_cards_filter(self.model, CardTypeFilter(sType))
            if len(aList) > 0 and aList[0] in self.aLibrary:
                self.dCardTypes[sType] = set([oC.name for oC in aList])

        for sFunction in CardFunctionFilter.get_values():
            aList = get_cards_filter(self.model, CardFunctionFilter(sFunction))
            if len(aList) > 0:
                self.dCardProperties[sFunction] = set([oC.name for oC in
                    aList])

        return True

    def _clear_stats(self):
        super(OpeningHandSimulator, self)._clear_stats()
        self.aLibrary = []
        self.aCrypt = []
        self.iMoreLib = 0
        self.iMoreCrypt = 0

    def setup_crypt_view(self):
        """Format a column of the crypt stats"""
        dCrypt = {}
        iTot = len(self.aCrypt)

        for oCard in self.aCrypt:
            dCrypt.setdefault(oCard.name, 0)
            dCrypt[oCard.name] += 1

        dCardProbs = {}
        for sCardName, iCount in dCrypt.iteritems():
            dCardProbs[sCardName] = hypergeometric_mean(iCount, 4, iTot)

        return setup_ungrouped_view(dCardProbs, 4, 'Crypt Card')

    def _fill_stats(self, oDialog):
        """Fill in the stats from the draws"""
        dTypeProbs = {}
        dPropProbs = {}
        dLibProbs = self._get_lib_props()
        get_probs(dLibProbs, self.dCardTypes, dTypeProbs)
        get_probs(dLibProbs, self.dCardProperties, dPropProbs)
        # setup display widgets
        oHBox = gtk.HBox(True, 3)
        # pylint: disable-msg=E1101
        # vbox methods not detected by pylint
        oDialog.vbox.pack_start(oHBox)
        oHBox.pack_start(setup_grouped_view(dLibProbs, dTypeProbs,
                                            7, 'Card Types'))
        oHBox.pack_start(setup_grouped_view(dLibProbs, dPropProbs, 7,
                                            'Card Properties'))
        oHBox.pack_start(self.setup_crypt_view())
        oHBox.show_all()

    def _get_lib_props(self):
        """Calculate the expected number of each card in the opening hand"""
        dLibCount = {}
        for oCard in self.aLibrary:
            dLibCount.setdefault(oCard.name, 0)
            dLibCount[oCard.name] += 1
        dLibProbs = {}
        iTot = len(self.aLibrary)
        for sName, iCount in dLibCount.iteritems():
            dLibProbs[sName] = hypergeometric_mean(iCount, 7, iTot)
        return dLibProbs

    def _draw_new_hand(self):
        """Create a new sample hand"""
        self.iCurHand += 1
        aThisLib = copy(self.aLibrary)
        aThisCrypt = copy(self.aCrypt)
        dHand = {}
        dProps = {}
        dTypes = {}
        draw_x_cards(aThisLib, 7, dHand)
        for sCard, iCount in dHand.iteritems():
            check_card(sCard, self.dCardTypes, dTypes, iCount)
            check_card(sCard, self.dCardProperties, dProps, iCount)
        dCrypt = {}
        draw_x_cards(aThisCrypt, 4, dCrypt)
        dNextHand = {}
        dNextCrypt = {}
        for iNextDraw in range(3):
            dNextHand[iNextDraw] = {}
            dNextCrypt[iNextDraw] = {}
            draw_x_cards(aThisLib, 5, dNextHand[iNextDraw])
            draw_x_cards(aThisCrypt, 1, dNextCrypt[iNextDraw])

        self.aDrawnHands.append([format_dict(dHand),
            fill_string(dTypes, dHand, self.dCardTypes),
            fill_string(dProps, dHand, self.dCardProperties),
            format_dict(dCrypt), dNextHand, dNextCrypt])
        return self._redraw_hand()

    def _redraw_hand(self):
        """Create a gtk.HBox holding a hand"""
        self.iMoreLib = 0
        self.iMoreCrypt = 0
        oHandBox = gtk.VBox(False, 2)
        oDrawLabel = gtk.Label()
        oHBox = gtk.HBox()
        oHandLabel = gtk.Label()
        oDrawLabel.set_markup('<b>Hand Number %d :</b>' % self.iCurHand)
        oHandLabel.set_markup(self.aDrawnHands[self.iCurHand - 1][0])
        oCryptLabel = gtk.Label()
        oCryptLabel.set_markup(self.aDrawnHands[self.iCurHand - 1][3])
        oHandBox.pack_start(oDrawLabel, False, False)
        oAlign = gtk.Alignment(xalign=0.5, xscale=0.7)
        oAlign.add(gtk.HSeparator())
        oHandBox.pack_start(oAlign, False, False)

        oCryptInfoBox = gtk.VBox(False, 0)
        oHandInfoBox = gtk.VBox(False, 0)
        oHandInfoBox.pack_start(oHandLabel, True, True)
        oMoreCards = gtk.Button('Next 5')
        oMoreCards.connect('clicked', self._more_lib, oHandInfoBox)
        oHandInfoBox.pack_start(oMoreCards, False, False)

        oCryptInfoBox.pack_start(oCryptLabel, True, True)
        oMoreCrypt = gtk.Button('Next 1')
        oMoreCrypt.connect('clicked', self._more_crypt, oCryptInfoBox)
        oCryptInfoBox.pack_start(oMoreCrypt, False, False)
        oFrame = gtk.Frame('Opening Hand')
        oFrame.add(oHandInfoBox)
        oHBox.pack_start(oFrame)
        oFrame = gtk.Frame('Opening Crypt Draw')
        oFrame.add(oCryptInfoBox)
        oHBox.pack_start(oFrame)
        oHandBox.pack_start(oHBox)
        return oHandBox

    def _more_lib(self, oButton, oBox):
        """Add the next 5 library cards"""
        if self.iMoreLib < 3:
            dNextHand = \
                    self.aDrawnHands[self.iCurHand - 1][4][self.iMoreLib]
            # pop out button show we can add our text
            oCardLabel = gtk.Label()
            oCardLabel.set_markup(format_dict(dNextHand))
            oBox.remove(oButton)
            oBox.pack_start(oCardLabel, True, True)
            self.iMoreLib += 1
            if self.iMoreLib < 3:
                oBox.pack_start(oButton, False, False)
            oBox.show_all()

    def _more_crypt(self, oButton, oBox):
        """Add the next crypt card"""
        if self.iMoreCrypt < 3:
            dNextCrypt = \
                    self.aDrawnHands[self.iCurHand - 1][5][self.iMoreCrypt]
            # pop out button show we can add our text
            oCardLabel = gtk.Label()
            oCardLabel.set_markup(format_dict(dNextCrypt))
            oBox.remove(oButton)
            oBox.pack_start(oCardLabel, True, True)
            self.iMoreCrypt += 1
            if self.iMoreCrypt < 3:
                oBox.pack_start(oButton, False, False)
            oBox.show_all()

    def _redraw_detail_box(self):
        """Fill in the details for the given hand"""
        def fill_frame(sDetails, sHeading):
            """Draw a gtk.Frame for the given detail type"""
            oFrame = gtk.Frame(sHeading)
            oLabel = gtk.Label()
            oLabel.set_markup(sDetails)
            oFrame.add(oLabel)
            return oFrame
        oDetailBox = gtk.VBox(False, 2)
        oHBox = gtk.HBox(False, 2)
        oHBox.pack_start(fill_frame(self.aDrawnHands[self.iCurHand - 1][1],
            'Card Types'))
        oHBox.pack_start(fill_frame(self.aDrawnHands[self.iCurHand - 1][2],
            'Card Properties'))
        oDetailBox.pack_start(oHBox)
        return oDetailBox

plugin = OpeningHandSimulator
