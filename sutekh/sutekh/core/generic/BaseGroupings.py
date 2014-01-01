# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Generic parts of the Groupings implementation"""

# Base Grouping Class

class IterGrouping(object):
    """Bass class for the groupings"""
    def __init__(self, oIter, fKeys):
        """Create the grouping

           oIter: Iterable to group.
           fKeys: Function which maps an item from the iterable
                  to a list of keys. Keys must be hashable.
           """
        self.__oIter = oIter
        self.__fKeys = fKeys

    def __iter__(self):
        dKeyItem = {}
        for oItem in self.__oIter:
            aSet = set(self.__fKeys(oItem))
            if len(aSet) == 0:
                dKeyItem.setdefault(None, []).append(oItem)
            else:
                for oKey in aSet:
                    dKeyItem.setdefault(oKey, []).append(oItem)

        aList = dKeyItem.keys()
        aList.sort()

        for oKey in aList:
            yield oKey, dKeyItem[oKey]

# Individual Groupings
#
# If you need to group PhysicalCards,
# set fGetCard to lambda x: x.abstractCard

# pylint: disable-msg=E0602
# pylint is confused by the lambda x: x construction
DEF_GET_CARD = lambda x: x
# pylint: enable-msg=E0602

# These are common enough to be generic


# pylint: disable-msg=C0111
# class names are pretty self-evident, so skip docstrings
class CardTypeGrouping(IterGrouping):
    def __init__(self, oIter, fGetCard=DEF_GET_CARD):
        super(CardTypeGrouping, self).__init__(oIter,
                lambda x: [y.name for y in fGetCard(x).cardtype])


class ExpansionGrouping(IterGrouping):
    def __init__(self, oIter, fGetCard=DEF_GET_CARD):
        super(ExpansionGrouping, self).__init__(oIter,
                lambda x: [y.expansion.name for y in fGetCard(x).rarity])


class RarityGrouping(IterGrouping):
    def __init__(self, oIter, fGetCard=DEF_GET_CARD):
        super(RarityGrouping, self).__init__(oIter,
                lambda x: [y.rarity.name for y in fGetCard(x).rarity])


class ArtistGrouping(IterGrouping):
    """Group by Artist"""
    def __init__(self, oIter, fGetCard=DEF_GET_CARD):
        super(ArtistGrouping, self).__init__(oIter,
            lambda x: [y.name for y in fGetCard(x).artists])


class KeywordGrouping(IterGrouping):
    """Group by Keyword"""
    def __init__(self, oIter, fGetCard=DEF_GET_CARD):
        super(KeywordGrouping, self).__init__(oIter,
            lambda x: [y.keyword for y in fGetCard(x).keywords])


class NullGrouping(IterGrouping):
    """Group everything into a single group named 'All'."""
    def __init__(self, oIter, _fGetCard=DEF_GET_CARD):
        super(NullGrouping, self).__init__(oIter, lambda x: ["All"])
