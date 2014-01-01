# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2005, 2006, 2007 Simon Cross <hodgestar@gmail.com>
# Copyright 2006, 2007 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

# pylint: disable-msg=W0231, W0223, C0302
# W0231 - the base classes don't have useful __init__ methods, so we
# generally don't call __init__ when creating a new filter
# W0223 - not every abstract method is immediately overridden
# C0302 - the module is long, but keeping the filters together is the best
# option

"""Define all the filters provided in sutekh"""

from sutekh.core.Objects import (AbstractCard, IAbstractCard, ICreed,
        IVirtue, IClan, IDiscipline, IExpansion, ITitle, ISect, ICardType,
        IPhysicalCardSet, IRarityPair, IRarity, Clan,
        Discipline, CardType, Title, Creed, Virtue, Sect, Expansion,
        RarityPair, PhysicalCardSet, PhysicalCard, IDisciplinePair,
        MapPhysicalCardToPhysicalCardSet, Artist, Keyword, IArtist, IKeyword,
        CRYPT_TYPES)
from sqlobject import SQLObjectNotFound, AND, OR, NOT, LIKE, func
from sqlobject.sqlbuilder import (Table, Alias, LEFTJOINOn, Select,
        SQLTrueClause as TRUE)
import string

from sutekh.core.generic.BaseFilters import (IN, Filter, FilterBox, FilterAndBox,
        FilterOrBox, FilterNot, NullFilter, SingleFilter, MultiFilter,
        DirectFilter, split_list, make_table_alias, AbstractCardFilter,
        PhysicalCardFilter, SpecificCardFilter, SpecificCardIdFilter,
        SpecificPhysCardIdFilter, CardNameFilter, CardSetMultiCardCountFilter,
        PhysicalCardSetFilter, MultiPhysicalCardSetFilter,
        MultiPhysicalCardSetMapFilter, PhysicalCardSetInUseFilter,
        CardSetNameFilter, CardSetDescriptionFilter, CardSetAuthorFilter,
        CardSetAnnotationsFilter, ParentCardSetFilter,
        CSPhysicalCardSetInUseFilter, ExpansionFilter, ExpansionRarityFilter,
        MultiExpansionRarityFilter, KeywordFilter, MultiKeywordFilter,
        AbstractCardFilter, CardTypeFilter, MultiCardTypeFilter,
        ArtistFilter, MultiArtistFilter, MultiExpansionFilter,
        PhysicalExpansionFilter, MultiPhysicalExpansionFilter,
        MultiSpecificCardIdFilter, CachedFilter)

# Individual Filters
class ClanFilter(SingleFilter):
    """Filter on Card's clan"""
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, sClan):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        self._oId = IClan(sClan).id
        self._oMapTable = make_table_alias('abs_clan_map')
        self._oIdField = self._oMapTable.q.clan_id


class MultiClanFilter(MultiFilter):
    """Filter on multiple clans"""
    keyword = "Clan"
    islistfilter = True
    description = "Clan"
    helptext = "a list of clans\nReturns all cards which require or are of" \
             " the specified clans"
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, aClans):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        self._aIds = [IClan(x).id for x in aClans]
        self._oMapTable = make_table_alias('abs_clan_map')
        self._oIdField = self._oMapTable.q.clan_id

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    @classmethod
    def get_values(cls):
        return [x.name for x in Clan.select().orderBy('name')]


class DisciplineFilter(MultiFilter):
    """Filter on a card's disciplines"""
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, sDiscipline):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        self._aIds = [oP.id for oP in IDiscipline(sDiscipline).pairs]
        self._oMapTable = make_table_alias('abs_discipline_pair_map')
        self._oIdField = self._oMapTable.q.discipline_pair_id


class MultiDisciplineFilter(MultiFilter):
    """Filter on multiple disciplines"""
    keyword = "Discipline"
    description = "Discipline"
    helptext = "a list of disciplines.\nReturns a list of all cards which " \
            "have or require the selected disciplines."
    islistfilter = True
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, aDisciplines):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        oPairs = []
        for sDis in aDisciplines:
            oPairs += IDiscipline(sDis).pairs
        self._aIds = [oP.id for oP in oPairs]
        self._oMapTable = make_table_alias('abs_discipline_pair_map')
        self._oIdField = self._oMapTable.q.discipline_pair_id

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    @classmethod
    def get_values(cls):
        return [x.fullname for x in Discipline.select().orderBy('name')]


class DisciplineLevelFilter(MultiFilter):
    """Filter on discipline & level combo"""
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, tDiscLevel):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        sDiscipline, sLevel = tDiscLevel
        sLevel = sLevel.lower()
        assert sLevel in ('inferior', 'superior')
        # There will be 0 or 1 ids
        self._aIds = [oP.id for oP in IDiscipline(sDiscipline).pairs if
                oP.level == sLevel]
        self._oMapTable = make_table_alias('abs_discipline_pair_map')
        self._oIdField = self._oMapTable.q.discipline_pair_id


class MultiDisciplineLevelFilter(MultiFilter):
    """Filter on multiple discipline & level combos"""
    keyword = "Discipline_with_Level"
    description = "Discipline with Level"
    helptext = "a list of disciplines with levels (each element specified" \
            " as a discipline with associated level, i.e. superior or" \
            " inferior)\nReturns all matching cards."
    iswithfilter = True
    islistfilter = True
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, aDiscLevels):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        self._aIds = []
        if isinstance(aDiscLevels[0], basestring):
            aValues = split_list(aDiscLevels)
        else:
            aValues = aDiscLevels
        for sDiscipline, sLevel in aValues:
            sLevel = sLevel.lower()
            assert sLevel in ('inferior', 'superior')
            self._aIds.extend([oP.id for oP in IDiscipline(sDiscipline).pairs
                    if oP.level == sLevel])
        self._oMapTable = make_table_alias('abs_discipline_pair_map')
        self._oIdField = self._oMapTable.q.discipline_pair_id

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    @classmethod
    def get_values(cls):
        oTemp = MultiDisciplineFilter([])
        aDisciplines = oTemp.get_values()
        aResults = []
        for sDisc in aDisciplines:
            for sLevel in ('inferior', 'superior'):
                try:
                    # Check if the discipline pair exists
                    IDisciplinePair((sDisc, sLevel))
                except SQLObjectNotFound:
                    continue  # No, so skip this case
                aResults.append('%s with %s' % (sDisc, sLevel))
        return aResults


class CryptCardFilter(MultiFilter):
    """Filter on crypt card types"""
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        self._aIds = [ICardType(x).id for x in CRYPT_TYPES]
        self._oMapTable = make_table_alias('abs_type_map')
        self._oIdField = self._oMapTable.q.card_type_id


class SectFilter(SingleFilter):
    """Filter on Sect"""
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, sSect):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        self._oId = ISect(sSect).id
        self._oMapTable = make_table_alias('abs_sect_map')
        self._oIdField = self._oMapTable.q.sect_id


class MultiSectFilter(MultiFilter):
    """Filter on Multiple Sects"""
    keyword = "Sect"
    description = "Sect"
    helptext = "a list of sects.\nReturns all cards belonging to the given" \
            " sects"
    islistfilter = True
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, aSects):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        self._aIds = [ISect(x).id for x in aSects]
        self._oMapTable = make_table_alias('abs_sect_map')
        self._oIdField = self._oMapTable.q.sect_id

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    @classmethod
    def get_values(cls):
        return [x.name for x in Sect.select().orderBy('name')]


class TitleFilter(SingleFilter):
    """Filter on Title"""
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, sTitle):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        self._oId = ITitle(sTitle).id
        self._oMapTable = make_table_alias('abs_title_map')
        self._oIdField = self._oMapTable.q.title_id


class MultiTitleFilter(MultiFilter):
    """Filter on Multiple Titles"""
    keyword = "Title"
    description = "Title"
    helptext = "a list of titles.\nReturns all cards with the selected titles."
    islistfilter = True
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, aTitles):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        self._aIds = [ITitle(x).id for x in aTitles]
        self._oMapTable = make_table_alias('abs_title_map')
        self._oIdField = self._oMapTable.q.title_id

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    @classmethod
    def get_values(cls):
        return [x.name for x in Title.select().orderBy('name')]


class CreedFilter(SingleFilter):
    """Filter on Creed"""
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, sCreed):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        self._oId = ICreed(sCreed).id
        self._oMapTable = make_table_alias('abs_creed_map')
        self._oIdField = self._oMapTable.q.creed_id


class MultiCreedFilter(MultiFilter):
    """Filter on Multiple Creed"""
    keyword = "Creed"
    description = "Creed"
    helptext = "a list of creeds.\nReturns all cards requiring or of the" \
            " selected creeds"
    islistfilter = True
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, aCreeds):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        self._aIds = [ICreed(x).id for x in aCreeds]
        self._oMapTable = make_table_alias('abs_creed_map')
        self._oIdField = self._oMapTable.q.creed_id

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    @classmethod
    def get_values(cls):
        return [x.name for x in Creed.select().orderBy('name')]


class VirtueFilter(SingleFilter):
    """Filter on Virtue"""
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, sVirtue):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        self._oId = IVirtue(sVirtue).id
        self._oMapTable = make_table_alias('abs_virtue_map')
        self._oIdField = self._oMapTable.q.virtue_id


class MultiVirtueFilter(MultiFilter):
    """Filter on Multiple Virtues"""
    keyword = "Virtue"
    description = "Virtue"
    helptext = "a list of virtues.\nReturns all cards requiring or having " \
            "the selected virtues"
    islistfilter = True
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, aVirtues):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        self._aIds = [IVirtue(x).id for x in aVirtues]
        self._oMapTable = make_table_alias('abs_virtue_map')
        self._oIdField = self._oMapTable.q.virtue_id

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    @classmethod
    def get_values(cls):
        return [x.fullname for x in Virtue.select().orderBy('name')]


class GroupFilter(DirectFilter):
    """Filter on Group"""
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, iGroup):
        self.__iGroup = iGroup

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    def _get_expression(self):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        return AbstractCard.q.group == self.__iGroup


class MultiGroupFilter(DirectFilter):
    """Filter on multiple Groups"""
    keyword = "Group"
    description = "Group"
    helptext = "a list of groups.\nReturns all cards belonging to the " \
            "listed group."
    islistfilter = True
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, aGroups):
        self.__aGroups = [int(sV) for sV in aGroups if sV != 'Any']
        if 'Any' in aGroups:
            self.__aGroups.append(-1)

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    @classmethod
    def get_values(cls):
        # pylint: disable-msg=E1101
        # E1101 - avoid SQLObject method not detected problems
        iMax = AbstractCard.select().max(AbstractCard.q.group)
        return [str(x) for x in range(1, iMax + 1)] + ['Any']

    def _get_expression(self):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        return IN(AbstractCard.q.group, self.__aGroups)


class CapacityFilter(DirectFilter):
    """Filter on Capacity"""
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, iCap):
        self.__iCap = iCap

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    def _get_expression(self):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        return AbstractCard.q.capacity == self.__iCap


class MultiCapacityFilter(DirectFilter):
    """Filter on a list of Capacities"""
    keyword = "Capacity"
    description = "Capacity"
    helptext = "a list of capacities.\nReturns all cards of the selected" \
            " capacities"
    islistfilter = True
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, aCaps):
        self.__aCaps = [int(sV) for sV in aCaps]

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    @classmethod
    def get_values(cls):
        # pylint: disable-msg=E1101
        # E1101 - avoid SQLObject method not detected problems
        iMax = AbstractCard.select().max(AbstractCard.q.capacity)
        return [str(x) for x in range(1, iMax + 1)]

    def _get_expression(self):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        return IN(AbstractCard.q.capacity, self.__aCaps)


class CostFilter(DirectFilter):
    """Filter on Cost"""
    types = ('AbstractCard', 'PhysicalCard')

    # Should this exclude Vamps & Imbued, if we search for
    # cards without cost?
    def __init__(self, iCost):
        self.__iCost = iCost
        # Handle 0 correctly
        if not iCost:
            self.__iCost = None

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    def _get_expression(self):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        return AbstractCard.q.cost == self.__iCost


class MultiCostFilter(DirectFilter):
    """Filter on a list of Costs"""
    keyword = "Cost"
    description = "Cost"
    helptext = "a list of costs.\nReturns all cards with the given costs."
    islistfilter = True
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, aCost):
        self.__aCost = [int(sV) for sV in aCost if sV != 'X']
        self.__bZeroCost = False
        if 'X' in aCost:
            self.__aCost.append(-1)
        if 0 in self.__aCost:
            self.__bZeroCost = True
            self.__aCost.remove(0)

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    @classmethod
    def get_values(cls):
        # pylint: disable-msg=E1101
        # E1101 - avoid SQLObject method not detected problems
        iMax = AbstractCard.select().max(AbstractCard.q.cost)
        return [str(x) for x in range(0, iMax + 1)] + ['X']

    def _get_expression(self):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        if self.__bZeroCost:
            if self.__aCost:
                return OR(IN(AbstractCard.q.cost, self.__aCost),
                        AbstractCard.q.cost == None)
            else:
                return AbstractCard.q.cost == None
        return IN(AbstractCard.q.cost, self.__aCost)


class CostTypeFilter(DirectFilter):
    """Filter on cost type"""
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, sCostType):
        self.__sCostType = sCostType.lower()
        assert self.__sCostType in ("blood", "pool", "conviction", None)

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    def _get_expression(self):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        return AbstractCard.q.costtype == self.__sCostType.lower()


class MultiCostTypeFilter(DirectFilter):
    """Filter on a list of cost types"""
    keyword = "CostType"
    islistfilter = True
    description = "Cost Type"
    helptext = "a list of cost types.\nReturns cards requiring the selected" \
            " cost types."
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, aCostTypes):
        self.__aCostTypes = [x.lower() for x in aCostTypes if x is not None]
        for sCostType in self.__aCostTypes:
            assert sCostType in ("blood", "pool", "conviction")
        if None in aCostTypes:
            self.__aCostTypes.append(None)

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    @classmethod
    def get_values(cls):
        return ["blood", "pool", "conviction"]

    def _get_expression(self):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        return IN(AbstractCard.q.costtype, self.__aCostTypes)


class LifeFilter(DirectFilter):
    """Filter on life"""
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, iLife):
        self.__iLife = iLife

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    def _get_expression(self):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        return AbstractCard.q.life == self.__iLife


class MultiLifeFilter(DirectFilter):
    """Filter on a list of list values"""
    keyword = "Life"
    description = "Life"
    helptext = "a list of life values.\nReturns allies (both library and " \
            "crypt cards) and retainers with the selected life.\n" \
            "For cases where the life varies, only the base value for life " \
            "is used."
    islistfilter = True
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, aLife):
        self.__aLife = [int(sV) for sV in aLife]

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    @classmethod
    def get_values(cls):
        # pylint: disable-msg=E1101
        # E1101 - avoid SQLObject method not detected problems
        iMax = AbstractCard.select().max(AbstractCard.q.life)
        return [str(x) for x in range(1, iMax + 1)]

    def _get_expression(self):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        return IN(AbstractCard.q.life, self.__aLife)


class CardTextFilter(DirectFilter):
    """Filter on Card Text"""
    keyword = "CardText"
    description = "Card Text"
    helptext = "the desired card text to search for (% can be used as a " \
            "wildcard).\nReturns all cards whose text contains this string."
    istextentry = True
    types = ('AbstractCard', 'PhysicalCard')

    def __init__(self, sPattern):
        self.__sPattern = sPattern.lower().encode('utf-8')
        self.__bBraces = '{' in self.__sPattern or '}' in self.__sPattern

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    @classmethod
    def get_values(cls):
        return ''

    def _get_expression(self):
        # pylint: disable-msg=E1101
        # SQLObject methods not detected by pylint
        if self.__bBraces:
            return LIKE(func.LOWER(AbstractCard.q.text),
                    '%' + self.__sPattern + '%')
        return LIKE(func.LOWER(AbstractCard.q.search_text),
                '%' + self.__sPattern + '%')


class CardFunctionFilter(DirectFilter):
    """Filter for various interesting card properties - untap, stealth, etc."""
    keyword = "CardFunction"
    description = "Card Function"
    helptext = "the chosen function from the list of supported types.\n" \
            "Functions include roles such as untap or bleed modifier.\n" \
            "Returns all cards matching the given functions."
    islistfilter = True
    types = ('AbstractCard', 'PhysicalCard')

    # Currently mainly used by the Hand Simulation plugin

    # Implementation discussion
    # Because we want flexiblity here, we define these filters in terms
    # of the existing filters - this avoids needing fancy
    # logic in _get_joins, and so forth
    # The filters can only be specificed after the database connection is
    # established, hence the list of constants and if .. constuction
    # in __init__, rather than using a class dictionary or similiar scheme

    __sStealth = 'Stealth action modifiers'
    __sIntercept = 'Intercept reactions'
    __sUntap = 'Untap reactions (Wake)'
    __sBounce = 'Bleed redirection reactions (Bounce)'
    __sEnterCombat = 'Enter combat actions (Rush)'
    __sBleedModifier = 'Increased bleed action modifiers'
    __sBleedAction = 'Increased bleed actions'
    __sBleedReduction = 'Bleed reduction reactions'

    def __init__(self, aTypes):
        aFilters = []
        if self.__sStealth in aTypes:
            aFilters.append(FilterAndBox([CardTypeFilter('Action Modifier'),
                CardTextFilter('+_ stealth')]))
        if self.__sIntercept in aTypes:
            aFilters.append(FilterAndBox([CardTypeFilter('Reaction'),
                CardTextFilter('+_ intercept')]))
        if self.__sUntap in aTypes:
            aFilters.append(FilterAndBox([CardTypeFilter('Reaction'),
                FilterOrBox([CardTextFilter('this vampire untaps'),
                    CardTextFilter('this reacting vampire untaps'),
                    CardTextFilter('untap this vampire'),
                    CardTextFilter('untap this reacting vampire'),
                    CardTextFilter('as though untapped')])]))
        if self.__sBounce in aTypes:
            aFilters.append(FilterAndBox([CardTypeFilter('Reaction'),
                CardTextFilter('is now bleeding')]))
        if self.__sEnterCombat in aTypes:
            aFilters.append(FilterAndBox([CardTypeFilter('Action'),
                CardTextFilter('(D) Enter combat')]))
        if self.__sBleedModifier in aTypes:
            aFilters.append(FilterAndBox([CardTypeFilter('Action Modifier'),
                CardTextFilter('+_ bleed')]))
        if self.__sBleedAction in aTypes:
            aFilters.append(FilterAndBox([CardTypeFilter('Action'),
                FilterOrBox([CardTextFilter('(D) bleed%at +_ bleed'),
                    CardTextFilter('(D) bleed%with +_ bleed')])]))
        if self.__sBleedReduction in aTypes:
            # Ordering of bleed and reduce not consistent, so we
            # use an AND filter, rather than 'reduce%bleed'
            aFilters.append(FilterAndBox([CardTypeFilter('Reaction'),
                CardTextFilter('bleed'), CardTextFilter('reduce')]))
        self._oFilter = FilterOrBox(aFilters)

    # pylint: disable-msg=C0111
    # don't need docstrings for _get_expression, get_values & _get_joins
    @classmethod
    def get_values(cls):
        """Values supported by this filter"""
        aVals = sorted([cls.__sStealth, cls.__sIntercept, cls.__sUntap,
            cls.__sBounce, cls.__sEnterCombat, cls.__sBleedModifier,
            cls.__sBleedAction, cls.__sBleedReduction,
            ])
        return aVals

    # pylint: disable-msg=W0212
    # we access protexted members intentionally
    def _get_joins(self):
        """Joins for the constructed filter"""
        return self._oFilter._get_joins()

    def _get_expression(self):
        """Expression for the constructed filter"""
        return self._oFilter._get_expression()


def make_illegal_filter():
    """Creates a filter that excludes not legal for tournament play cards.

       Handles the case that the keyword hasn't been updated yet correctly."""
    oLegalFilter = NullFilter()
    try:
        # We use MultiKeywordFilter to work around a performance
        # oddity of sqlite, where IN(a, b) outperforms a == b
        # for large sets
        oLegalFilter = FilterNot(MultiKeywordFilter(['not for legal play']))
    except SQLObjectNotFound:
        oLegalFilter = FilterNot(CardTextFilter(
            'Added to the V:EKN banned list'))
    return oLegalFilter


def best_guess_filter(sName):
    """Create a filter for selecting close matches to a card name."""
    # Set the filter on the Card List to one the does a
    # Best guess search
    sFilterString = ' ' + sName.lower() + ' '
    # Kill the's in the string
    sFilterString = sFilterString.replace(' the ', ' ')
    # Kill commas, as possible issues
    sFilterString = sFilterString.replace(',', ' ')
    # Free style punctuation
    for sPunc in string.punctuation:
        sFilterString = sFilterString.replace(sPunc, '_')
    # Stolen semi-concept from soundex - replace vowels with wildcards
    # Should these be %'s ??
    # (Should at least handle the Rotscheck variation as it stands)
    sFilterString = sFilterString.replace('a', '_')
    sFilterString = sFilterString.replace('e', '_')
    sFilterString = sFilterString.replace('i', '_')
    sFilterString = sFilterString.replace('o', '_')
    sFilterString = sFilterString.replace('u', '_')
    # Normalise spaces and Wildcard spaces
    sFilterString = ' '.join(sFilterString.split())
    sFilterString = sFilterString.replace(' ', '%')
    # Add % on outside
    sFilterString = '%' + sFilterString + '%'
    oLegalFilter = make_illegal_filter()
    return FilterAndBox([CardNameFilter(sFilterString), oLegalFilter])


# The List of filters exposed to the Filter Parser - new filters should just
# be tacked on here
PARSER_FILTERS = (
        MultiCardTypeFilter, MultiCostTypeFilter, MultiClanFilter,
        MultiDisciplineFilter, MultiGroupFilter, MultiCapacityFilter,
        MultiCostFilter, MultiLifeFilter, MultiCreedFilter, MultiVirtueFilter,
        CardTextFilter, CardNameFilter, MultiSectFilter, MultiTitleFilter,
        MultiExpansionRarityFilter, MultiDisciplineLevelFilter,
        MultiPhysicalExpansionFilter, CardSetNameFilter, CardSetAuthorFilter,
        CardSetDescriptionFilter, CardSetAnnotationsFilter,
        MultiPhysicalCardSetFilter, PhysicalCardSetInUseFilter,
        CardSetMultiCardCountFilter, CSPhysicalCardSetInUseFilter,
        CardFunctionFilter, ParentCardSetFilter, MultiArtistFilter,
        MultiKeywordFilter,
        )
