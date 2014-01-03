# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Allow the use to change how the cards are grouped in the CardListView"""

from sutekh.core.Objects import PhysicalCard, PhysicalCardSet
from sutekh.core.Groupings import CardTypeGrouping, ClanGrouping, \
        DisciplineGrouping, ExpansionGrouping, RarityGrouping, \
        CryptLibraryGrouping, NullGrouping, MultiTypeGrouping, \
        SectGrouping, TitleGrouping, CostGrouping, GroupGrouping, \
        ArtistGrouping, KeywordGrouping, GroupPairGrouping, \
        DisciplineLevelGrouping
from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.gui.generic.baseplugins.BaseChangeGroupBy import BaseGroupCardList


class GroupCardList(SutekhPlugin, BaseGroupCardList):
    """Plugin to allow the user to change how cards are grouped.

       Show a dialog which allows the user to select from the avail
       groupings of the cards, and changes the setting in the CardListView.
       """

    GROUPINGS = {
        'Card Type': CardTypeGrouping,
        'Multi Card Type': MultiTypeGrouping,
        'Crypt or Library': CryptLibraryGrouping,
        'Clans and Creeds': ClanGrouping,
        'Disciplines and Virtues': DisciplineGrouping,
        'Disciplines (by level) and Virtues': DisciplineLevelGrouping,
        'Expansion': ExpansionGrouping,
        'Rarity': RarityGrouping,
        'Sect': SectGrouping,
        'Title': TitleGrouping,
        'Cost': CostGrouping,
        'Group': GroupGrouping,
        'Group pairs': GroupPairGrouping,
        'Artist': ArtistGrouping,
        'Keyword': KeywordGrouping,
        'No Grouping': NullGrouping,
    }

    OPTION_STR = ", ".join('"%s"' % sKey for sKey in GROUPINGS.keys())
    GROUP_BY = "group by"

    dTableVersions = {}
    aModelsSupported = (PhysicalCard, PhysicalCardSet)
    dPerPaneConfig = {
        GROUP_BY: 'option(%s, default="Card Type")' % OPTION_STR,
    }

    dCardListConfig = dPerPaneConfig


plugin = GroupCardList
