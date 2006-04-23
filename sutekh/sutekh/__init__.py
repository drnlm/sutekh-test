# __init__.py
# Copyright 2005,2006 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

__all__ = [ # Sutekh Objects
            'AbstractCard', 'PhysicalCard', 'AbstractCardSet', 'PhysicalCardSet',
            'RarityPair', 'Expansion', 'Rarity', 'DisciplinePair', 'Discipline',
            'Clan', 'CardType', 'Ruling',
            # Filters
            'FilterAndBox', 'FilterOrBox', 'ClanFilter', 'DisciplineFilter',
            'CardTypeFilter', 'CardTextFilter',
            # Groupings
            'GroupByCardType',
            # Misc
           'start' ]

# Do importing
from SutekhObjects import *
from Filters import *
from Groupings import *
from SutekhCli import main

# start() method for use when working in the Python interpreter
def start(aArgs=['sutekh']):
    main(aArgs)
