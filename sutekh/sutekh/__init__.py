# __init__.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2005, 2006, 2007 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""This is the sutekh package.
   """

# Do importing

from sutekh.core.SutekhObjects import AbstractCard, PhysicalCard, \
                    PhysicalCardSet, RarityPair, \
                    Expansion, Rarity, DisciplinePair, Discipline, \
                    Clan, CardType, Ruling

from sutekh.core.Filters import FilterAndBox, FilterOrBox, ClanFilter, \
                    DisciplineFilter, CardTypeFilter, CardTextFilter, \
                    MultiCardTypeFilter, MultiDisciplineFilter, \
                    MultiClanFilter, PhysicalCardSetFilter, \
                    PhysicalCardFilter, GroupFilter, MultiGroupFilter, \
                    ExpansionFilter, MultiExpansionFilter, \
                    PhysicalExpansionFilter, \
                    MultiPhysicalExpansionFilter, CardSetNameFilter, \
                    CardSetDescriptionFilter, CardSetAuthorFilter, \
                    CardSetAnnotationsFilter

from sutekh.core.Groupings import CardTypeGrouping, ClanGrouping, \
                    DisciplineGrouping, ExpansionGrouping, \
                    RarityGrouping

from sutekh.core.CardListTabulator import CardListTabulator

from sutekh.SutekhCli import main

# start() method for use when working in the Python interpreter
# pylint: disable-msg=C0111, W0102

def start(aArgs=['sutekh']):
    main(aArgs)

# What we expose to import *

aAll = [ # Sutekh Objects
         AbstractCard, PhysicalCard, PhysicalCardSet,
         RarityPair, Expansion, Rarity, DisciplinePair, Discipline,
         Clan, CardType, Ruling,
         # Filters
         FilterAndBox, FilterOrBox, ClanFilter, DisciplineFilter,
         CardTypeFilter, CardTextFilter, MultiCardTypeFilter,
         MultiDisciplineFilter, MultiClanFilter, PhysicalCardSetFilter,
         PhysicalCardFilter, GroupFilter, MultiGroupFilter,
         ExpansionFilter, MultiExpansionFilter,
         CardSetNameFilter, CardSetAuthorFilter, CardSetDescriptionFilter,
         CardSetAnnotationsFilter, PhysicalExpansionFilter,
         MultiPhysicalExpansionFilter,
         # Groupings
         CardTypeGrouping, ClanGrouping, DisciplineGrouping,
         ExpansionGrouping, RarityGrouping,
         # Misc
         start, CardListTabulator ]

__all__ = [ x.__name__ for x in aAll ]


