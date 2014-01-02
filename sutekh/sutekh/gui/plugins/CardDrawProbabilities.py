# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Dialog to display deck analysis software
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>,
# GPL - see COPYING for details
"""Calculate probabilities for drawing the current selection."""

import gtk
from copy import copy
from sutekh.core.Objects import PhysicalCardSet, IAbstractCard
from sutekh.SutekhUtility import is_crypt_card
from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.gui.generic.baseplugins.BaseDrawProbabilities import BaseDrawSim


class CardDrawSimPlugin(SutekhPlugin, BaseDrawSim):
    """Displays the probabilities for drawing cards from the current
       selection."""
    dTableVersions = {PhysicalCardSet: (4, 5, 6)}
    aModelsSupported = (PhysicalCardSet,)

    def _check_selection(self, aSelectedCards):
        # Check that selection doesn't mix crypt and libraries
        bCrypt = False
        bLibrary = False
        _oModel, aSelection = self.view.get_selection().get_selected_rows()
        for oCard in aSelectedCards:
            if is_crypt_card(oCard):
                bCrypt = True
            else:
                bLibrary = True

        if bLibrary and bCrypt:
            do_complaint_error("Can't operate on selections including both"
                    " Crypt and Library cards")
            return False
        # Flag for later use
        self.bCrypt = bCrypt
        return True

    def _get_draw_label(self):
        if self.bCrypt:
            oLabel = gtk.Label('Opening Crypt Draw')
        else:
            oLabel = gtk.Label('Opening Hand')
        return oLabel

    def _set_draw_size(self):
        oMainTitle = gtk.Label()
        if self.bCrypt:
            oMainTitle.set_markup('<b>Crypt:</b> Drawing from <b>%d</b> '
                    'cards' % self.iTotal)
            self.iOpeningDraw = 4
            self.iNumSteps = min(2, self.iTotal - self.iOpeningDraw)
        else:
            oMainTitle.set_markup('<b>Library:</b> Drawing from <b>%d</b> '
                    'cards' % self.iTotal)
            self.iOpeningDraw = 7
            # Look 15 cards into the deck by default, seems good start
            self.iNumSteps = min(8, self.iTotal - self.iOpeningDraw)
        return oMainTitle

    def _complain_size(self):
        if self.bCrypt:
            do_complaint_error("Crypt must be larger than"
                               " the opening draw")
        else:
            do_complaint_error("Library must be larger than the opening"
                               " hand")

    def _setup_cardlists(self, aSelectedCards):
        """Extract the needed card info from the model"""
        iCryptSize = 0
        iLibrarySize = 0
        aAllAbsCards = self._get_card_counts(aSelectedCards)
        for oCard in aAllAbsCards:
            if is_crypt_card(oCard):
                iCryptSize += 1
            else:
                iLibrarySize += 1
        if self.bCrypt:
            self.iTotal = iCryptSize
        else:
            self.iTotal = iLibrarySize


plugin = CardDrawSimPlugin
