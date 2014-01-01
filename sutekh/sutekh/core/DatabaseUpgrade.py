# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2006, 2007, 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details
"""Handles the heavy lifting of upgrading the database.

   Holds methods to copy database contents around, utility classes
   to talk to old database versions, and so forth.

   We only support upgrading from the previous stable version
   (currently 0.8)
   """

# pylint: disable-msg=C0302
# This is a long module, partly because of the duplicated code from
# SutekhObjects. We want to keep all the database upgrade stuff together.
# so we jsut live with it

# pylint: disable-msg=E0611
# sqlobject confuses pylint here
from sqlobject import (sqlhub, SQLObject, IntCol, UnicodeCol, RelatedJoin,
        EnumCol, MultipleJoin, connectionForURI, ForeignKey, SQLObjectNotFound)
# pylint: enable-msg=E0611
from logging import Logger
from sutekh.core.Objects import (PhysicalCard, AbstractCard,
        PhysicalCardSet, Expansion, Clan, Virtue, Discipline, Rarity,
        RarityPair, CardType, Ruling, DisciplinePair, Creed,
        Sect, Title, Keyword, Artist, flush_cache, MAX_ID_LENGTH)
from sutekh.core.generic.CardSetHolder import CachedCardSetHolder
from sutekh.io.WhiteWolfTextParser import strip_braces
from sutekh.core.generic.DatabaseVersion import DatabaseVersion
from sutekh.core.generic.BaseDatabaseUpgrade import (UnknownVersion,
        copy_physical_card_set_loop, do_read_old_database,
        do_copy_database, make_card_set_holder, copy_to_new_abstract_card_db,
        do_create_memory_copy, do_create_final_copy,
        do_attempt_database_upgrade)

# This file handles all the grunt work of the database upgrades. We have some
# (arguablely overly) complex trickery to read old databases, and we create a
# copy in sqlite memory database first, before commiting to the actual DB

# We Need to clone the SQLObject classes in SutekhObjects so we can read
# old versions


# pylint: disable-msg=C0103, W0232
# C0103 - names set largely by SQLObject conventions, so ours don't apply
# W0232 - SQLObject classes don't have user defined __init__
class AbstractCard_v5(SQLObject):
    """Table used to upgrade AbstractCard from v5"""
    class sqlmeta:
        """meta class used to set the correct table"""
        table = AbstractCard.sqlmeta.table
        cacheValues = False

    canonicalName = UnicodeCol(alternateID=True, length=MAX_ID_LENGTH)
    name = UnicodeCol()
    text = UnicodeCol()
    group = IntCol(default=None, dbName='grp')
    capacity = IntCol(default=None)
    cost = IntCol(default=None)
    life = IntCol(default=None)
    costtype = EnumCol(enumValues=['pool', 'blood', 'conviction', None],
            default=None)
    level = EnumCol(enumValues=['advanced', None], default=None)

    # Most of these names are singular when they should be plural
    # since they refer to lists. We've decided to live with the
    # inconsistency for old columns but do the right thing for new
    # ones.
    discipline = RelatedJoin('DisciplinePair',
            intermediateTable='abs_discipline_pair_map',
            createRelatedTable=False)
    rarity = RelatedJoin('RarityPair',
            intermediateTable='abs_rarity_pair_map',
            createRelatedTable=False)
    clan = RelatedJoin('Clan',
            intermediateTable='abs_clan_map', createRelatedTable=False)
    cardtype = RelatedJoin('CardType', intermediateTable='abs_type_map',
            createRelatedTable=False)
    sect = RelatedJoin('Sect', intermediateTable='abs_sect_map',
            createRelatedTable=False)
    title = RelatedJoin('Title', intermediateTable='abs_title_map',
            createRelatedTable=False)
    creed = RelatedJoin('Creed', intermediateTable='abs_creed_map',
            createRelatedTable=False)
    virtue = RelatedJoin('Virtue', intermediateTable='abs_virtue_map',
            createRelatedTable=False)
    rulings = RelatedJoin('Ruling', intermediateTable='abs_ruling_map',
            createRelatedTable=False)
    artists = RelatedJoin('Artist', intermediateTable='abs_artist_map',
            createRelatedTable=False)
    keywords = RelatedJoin('Keyword',
            intermediateTable='abs_keyword_map', createRelatedTable=False)

    physicalCards = MultipleJoin('PhysicalCard')


class PhysicalCard_ACv5(SQLObject):
    """Table used to upgrade AbstractCard from v5"""
    class sqlmeta:
        """meta cleass used to set the correct table"""
        table = PhysicalCard.sqlmeta.table
        cacheValues = False

    abstractCard = ForeignKey('AbstractCard_v5')
    # Explicitly allow None as expansion
    expansion = ForeignKey('Expansion_v3', notNull=False)
    sets = RelatedJoin('PhysicalCardSet', intermediateTable='physical_map',
            createRelatedTable=False)


class Expansion_v3(SQLObject):
    """Table used to update Expansion from v3"""

    class sqlmeta:
        """meta cleass used to set the correct table"""
        table = Expansion.sqlmeta.table
        cacheValues = False

    name = UnicodeCol(alternateID=True, length=MAX_ID_LENGTH)
    shortname = UnicodeCol(default=None)
    pairs = MultipleJoin('RarityPair_Ev3')


class RarityPair_Ev3(SQLObject):
    """Table used to update Expansion from v3"""

    class sqlmeta:
        """meta cleass used to set the correct table"""
        table = RarityPair.sqlmeta.table
        cacheValues = False

    expansion = ForeignKey('Expansion_v3')
    rarity = ForeignKey('Rarity')


# pylint: enable-msg=C0103, W0232


def check_can_read_old_database(oConn):
    # pylint: disable-msg=R0912
    # This has to be a giant if .. elif statement to check all the classes
    # subdivision isn't really beneficial
    """Can we upgrade from this database version?

       Sutekh 0.9.x and 1.0.x can upgrade from the versions in Sutekh 0.8.x,
       but no earlier
       """
    oVer = DatabaseVersion()
    oVer.expire_cache()
    if not oVer.check_tables_and_versions([Rarity], [Rarity.tableversion],
            oConn):
        raise UnknownVersion("Rarity")
    if not oVer.check_tables_and_versions([Expansion],
            [Expansion.tableversion], oConn) \
            and not oVer.check_tables_and_versions([Expansion], [3], oConn):
        raise UnknownVersion("Expansion")
    if not oVer.check_tables_and_versions([Discipline],
            [Discipline.tableversion], oConn):
        raise UnknownVersion("Discipline")
    if not oVer.check_tables_and_versions([Clan], [Clan.tableversion],
            oConn):
        raise UnknownVersion("Clan")
    if not oVer.check_tables_and_versions([CardType], [CardType.tableversion],
            oConn):
        raise UnknownVersion("CardType")
    if not oVer.check_tables_and_versions([Creed], [Creed.tableversion],
            oConn):
        raise UnknownVersion("Creed")
    if not oVer.check_tables_and_versions([Virtue], [Virtue.tableversion],
            oConn):
        raise UnknownVersion("Virtue")
    if not oVer.check_tables_and_versions([Sect], [Sect.tableversion], oConn):
        raise UnknownVersion("Sect")
    if not oVer.check_tables_and_versions([Title], [Title.tableversion],
            oConn):
        raise UnknownVersion("Title")
    if not oVer.check_tables_and_versions([Keyword], [Keyword.tableversion],
            oConn):
        raise UnknownVersion("Keyword")
    if not oVer.check_tables_and_versions([Artist], [Artist.tableversion],
            oConn):
        raise UnknownVersion("Artist")
    if not oVer.check_tables_and_versions([Ruling], [Ruling.tableversion],
            oConn):
        raise UnknownVersion("Ruling")
    if not oVer.check_tables_and_versions([DisciplinePair],
            [DisciplinePair.tableversion], oConn):
        raise UnknownVersion("DisciplinePair")
    if not oVer.check_tables_and_versions([RarityPair],
            [RarityPair.tableversion], oConn):
        raise UnknownVersion("RarityPair")
    if not oVer.check_tables_and_versions([AbstractCard],
            [AbstractCard.tableversion], oConn) \
            and not oVer.check_tables_and_versions([AbstractCard], [5], oConn):
        raise UnknownVersion("AbstractCard")
    if not oVer.check_tables_and_versions([PhysicalCard],
            [PhysicalCard.tableversion], oConn):
        raise UnknownVersion("PhysicalCard")
    if not oVer.check_tables_and_versions([PhysicalCardSet],
            [PhysicalCardSet.tableversion], oConn):
        raise UnknownVersion("PhysicalCardSet")
    return True


def old_database_count(oConn):
    """Check number of items in old DB fro progress bars, etc."""
    oVer = DatabaseVersion()
    iCount = 14  # Card property tables
    if oVer.check_tables_and_versions([AbstractCard],
            [AbstractCard.tableversion], oConn):
        iCount += AbstractCard.select(connection=oConn).count()
    elif oVer.check_tables_and_versions([AbstractCard], [5], oConn):
        iCount += AbstractCard_v5.select(connection=oConn).count()
    if oVer.check_tables_and_versions([PhysicalCard],
            [PhysicalCard.tableversion], oConn):
        iCount += PhysicalCard.select(connection=oConn).count()
    if oVer.check_tables_and_versions([PhysicalCardSet],
            [PhysicalCardSet.tableversion], oConn):
        iCount += PhysicalCardSet.select(connection=oConn).count()
    return iCount


def new_database_count(oConn):
    return (14 + AbstractCard.select(connection=oConn).count() +
            PhysicalCard.select(connection=oConn).count() +
            PhysicalCardSet.select(connection=oConn).count())


def copy_rarity(oOrigConn, oTrans):
    """Copy rarity tables, assuming same version"""
    for oObj in Rarity.select(connection=oOrigConn):
        _oCopy = Rarity(id=oObj.id, name=oObj.name,
                shortname=oObj.shortname, connection=oTrans)


def copy_old_rarity(oOrigConn, oTrans, oVer):
    """Copy rarity table, upgrading versions as needed"""
    if oVer.check_tables_and_versions([Rarity], [Rarity.tableversion],
            oOrigConn):
        copy_rarity(oOrigConn, oTrans)
    else:
        return (False, ["Unknown Version for Rarity"])
    return (True, [])


def copy_expansion(oOrigConn, oTrans):
    """Copy expansion, assuming versions match"""
    for oObj in Expansion.select(connection=oOrigConn):
        _oCopy = Expansion(id=oObj.id, name=oObj.name,
                           shortname=oObj.shortname,
                           releasedate=oObj.releasedate,
                           connection=oTrans)


def copy_old_expansion(oOrigConn, oTrans, oVer):
    """Copy Expansion, updating as needed"""
    aMessages = []
    if oVer.check_tables_and_versions([Expansion], [Expansion.tableversion],
            oOrigConn):
        copy_expansion(oOrigConn, oTrans)
    elif oVer.check_tables_and_versions([Expansion], [3], oOrigConn):
        aMessages.append("Missing date information for expansions."
                         " You will need to reimport the card list"
                         " for these to be correct")
        for oObj in Expansion_v3.select(connection=oOrigConn):
            _oCopy = Expansion(id=oObj.id, name=oObj.name,
                               shortname=oObj.shortname,
                               releasedate=None,
                               connection=oTrans)
    else:
        return (False, ["Unknown Expansion Version"])
    return (True, aMessages)


def copy_discipline(oOrigConn, oTrans):
    """Copy Discipline, assuming versions match"""
    for oObj in Discipline.select(connection=oOrigConn):
        _oCopy = Discipline(id=oObj.id, name=oObj.name,
            fullname=oObj.fullname, connection=oTrans)


def copy_old_discipline(oOrigConn, oTrans, oVer):
    """Copy disciplines, upgrading as needed."""
    if oVer.check_tables_and_versions([Discipline], [Discipline.tableversion],
            oOrigConn):
        copy_discipline(oOrigConn, oTrans)
    else:
        return (False, ["Unknown Discipline version"])
    return (True, [])


def copy_clan(oOrigConn, oTrans):
    """Copy Clan, assuming database versions match"""
    for oObj in Clan.select(connection=oOrigConn):
        _oCopy = Clan(id=oObj.id, name=oObj.name, shortname=oObj.shortname,
                connection=oTrans)


def copy_old_clan(oOrigConn, oTrans, oVer):
    """Copy clan, upgrading as needed."""
    if oVer.check_tables_and_versions([Clan], [Clan.tableversion], oOrigConn):
        copy_clan(oOrigConn, oTrans)
    else:
        return (False, ["Unknown Clan Version"])
    return (True, [])


def copy_creed(oOrigConn, oTrans):
    """Copy Creed, assuming versions match"""
    for oObj in Creed.select(connection=oOrigConn):
        _oCopy = Creed(id=oObj.id, name=oObj.name, shortname=oObj.shortname,
                connection=oTrans)


def copy_old_creed(oOrigConn, oTrans, oVer):
    """Copy Creed, updating if needed"""
    if oVer.check_tables_and_versions([Creed], [Creed.tableversion],
            oOrigConn):
        copy_creed(oOrigConn, oTrans)
    else:
        return (False, ["Unknown Creed Version"])
    return (True, [])


def copy_virtue(oOrigConn, oTrans):
    """Copy Virtue, assuming versions match"""
    for oObj in Virtue.select(connection=oOrigConn):
        _oCopy = Virtue(id=oObj.id, name=oObj.name, fullname=oObj.fullname,
                connection=oTrans)


def copy_old_virtue(oOrigConn, oTrans, oVer):
    """Copy Virtue, updating if needed"""
    if oVer.check_tables_and_versions([Virtue], [Virtue.tableversion],
            oOrigConn):
        copy_virtue(oOrigConn, oTrans)
    else:
        return (False, ["Unknown Virtue Version"])
    return (True, [])


def copy_card_type(oOrigConn, oTrans):
    """Copy CardType, assuming versions match"""
    for oObj in CardType.select(connection=oOrigConn):
        _oCopy = CardType(id=oObj.id, name=oObj.name, connection=oTrans)


def copy_old_card_type(oOrigConn, oTrans, oVer):
    """Copy CardType, upgrading as needed"""
    if oVer.check_tables_and_versions([CardType], [CardType.tableversion],
            oOrigConn):
        copy_card_type(oOrigConn, oTrans)
    else:
        return (False, ["Unknown CardType Version"])
    return (True, [])


def copy_ruling(oOrigConn, oTrans):
    """Copy Ruling, assuming versions match"""
    for oObj in Ruling.select(connection=oOrigConn):
        _oCopy = Ruling(id=oObj.id, text=oObj.text, code=oObj.code,
                url=oObj.url, connection=oTrans)


def copy_old_ruling(oOrigConn, oTrans, oVer):
    """Copy Ruling, upgrading as needed"""
    if oVer.check_tables_and_versions([Ruling], [Ruling.tableversion],
            oOrigConn):
        copy_ruling(oOrigConn, oTrans)
    else:
        return (False, ["Unknown Ruling Version"])
    return (True, [])


def copy_discipline_pair(oOrigConn, oTrans):
    """Copy DisciplinePair, assuming versions match"""
    for oObj in DisciplinePair.select(connection=oOrigConn):
        # Force for SQLObject >= 0.11.4
        oObj._connection = oOrigConn
        _oCopy = DisciplinePair(id=oObj.id, level=oObj.level,
               discipline=oObj.discipline, connection=oTrans)


def copy_old_discipline_pair(oOrigConn, oTrans, oVer):
    """Copy DisciplinePair, upgrading if needed"""
    if oVer.check_tables_and_versions([DisciplinePair],
            [DisciplinePair.tableversion], oOrigConn):
        copy_discipline_pair(oOrigConn, oTrans)
    else:
        return (False, ["Unknown Discipline Version"])
    return (True, [])


def copy_rarity_pair(oOrigConn, oTrans):
    """Copy RairtyPair, assuming versions match"""
    for oObj in RarityPair.select(connection=oOrigConn):
        # Force for SQLObject >= 0.11.4
        oObj._connection = oOrigConn
        _oCopy = RarityPair(id=oObj.id, expansion=oObj.expansion,
                rarity=oObj.rarity, connection=oTrans)


def copy_old_rarity_pair(oOrigConn, oTrans, oVer):
    """Copy RarityPair, upgrading as needed"""
    if oVer.check_tables_and_versions([RarityPair], [RarityPair.tableversion],
            oOrigConn):
        if oVer.check_tables_and_versions([Expansion],
                                          [Expansion.tableversion],
                                          oOrigConn):
            copy_rarity_pair(oOrigConn, oTrans)
        elif oVer.check_tables_and_versions([Expansion], [3], oOrigConn):
            for oObj in RarityPair_Ev3.select(connection=oOrigConn):
                oObj._connection = oOrigConn
                _oCopy = RarityPair(id=oObj.id, expansionID=oObj.expansion.id,
                                    rarityID=oObj.rarity.id, connection=oTrans)
        else:
            # This may result in a duplicate error message
            return (False, ["Unknown Expansion version"])
    else:
        return (False, ["Unknown RarityPair version"])
    return (True, [])


def copy_sect(oOrigConn, oTrans):
    """Copy Sect, assuming versions match"""
    for oObj in Sect.select(connection=oOrigConn):
        _oCopy = Sect(id=oObj.id, name=oObj.name, connection=oTrans)


def copy_old_sect(oOrigConn, oTrans, oVer):
    """Copy Sect, updating if needed"""
    if oVer.check_tables_and_versions([Sect], [Sect.tableversion], oOrigConn):
        copy_sect(oOrigConn, oTrans)
    else:
        return (False, ["Unknown Sect Version"])
    return (True, [])


def copy_title(oOrigConn, oTrans):
    """Copy Title, assuming versions match"""
    for oObj in Title.select(connection=oOrigConn):
        _oCopy = Title(id=oObj.id, name=oObj.name, connection=oTrans)


def copy_old_title(oOrigConn, oTrans, oVer):
    """Copy Title, updating if needed"""
    if oVer.check_tables_and_versions([Title], [Title.tableversion],
            oOrigConn):
        copy_title(oOrigConn, oTrans)
    else:
        return (False, ["Unknown Title Version"])
    return (True, [])


def copy_keyword(oOrigConn, oTrans):
    """Copy Keyword, assuming versions match"""
    for oObj in Keyword.select(connection=oOrigConn):
        _oCopy = Keyword(id=oObj.id, keyword=oObj.keyword, connection=oTrans)


def copy_old_keyword(oOrigConn, oTrans, oVer):
    """Copy Keyword, updating if needed"""
    if oVer.check_tables_and_versions([Keyword], [Keyword.tableversion],
            oOrigConn):
        copy_keyword(oOrigConn, oTrans)
    else:
        return (False, ["Unknown Keyword Version"])
    return (True, [])


def copy_artist(oOrigConn, oTrans):
    """Copy Artist, assuming versions match"""
    for oObj in Artist.select(connection=oOrigConn):
        _oCopy = Artist(id=oObj.id, canonicalName=oObj.canonicalName,
            name=oObj.name, connection=oTrans)


def copy_old_artist(oOrigConn, oTrans, oVer):
    """Copy Artist, updating if needed"""
    if oVer.check_tables_and_versions([Artist], [Artist.tableversion],
            oOrigConn):
        copy_artist(oOrigConn, oTrans)
    else:
        return (False, ["Unknown Artist Version"])
    return (True, [])


def copy_abstract_card(oOrigConn, oTrans, oLogger):
    """Copy AbstractCard, assuming versions match"""
    # pylint: disable-msg=E1101, R0912
    # E1101 - SQLObject confuses pylint
    # R0912 - need the branches for this
    for oCard in AbstractCard.select(connection=oOrigConn):
        # force issue for SQObject >= 0.11.4
        oCard._connection = oOrigConn
        oCardCopy = AbstractCard(id=oCard.id,
                canonicalName=oCard.canonicalName, name=oCard.name,
                text=oCard.text, search_text=oCard.search_text,
                connection=oTrans)
        # If I don't do things this way, I get encoding issues
        # I don't really feel like trying to understand why
        oCardCopy.group = oCard.group
        oCardCopy.capacity = oCard.capacity
        oCardCopy.cost = oCard.cost
        oCardCopy.costtype = oCard.costtype
        oCardCopy.level = oCard.level
        oCardCopy.life = oCard.life
        for oData in oCard.rarity:
            oCardCopy.addRarityPair(oData)
        for oData in oCard.discipline:
            oCardCopy.addDisciplinePair(oData)
        for oData in oCard.rulings:
            oCardCopy.addRuling(oData)
        for oData in oCard.clan:
            oCardCopy.addClan(oData)
        for oData in oCard.cardtype:
            oCardCopy.addCardType(oData)
        for oData in oCard.sect:
            oCardCopy.addSect(oData)
        for oData in oCard.title:
            oCardCopy.addTitle(oData)
        for oData in oCard.creed:
            oCardCopy.addCreed(oData)
        for oData in oCard.virtue:
            oCardCopy.addVirtue(oData)
        for oData in oCard.keywords:
            oCardCopy.addKeyword(oData)
        for oData in oCard.artists:
            oCardCopy.addArtist(oData)
        oCardCopy.syncUpdate()
        oLogger.info('copied AC %s', oCardCopy.name)


def copy_old_abstract_card(oOrigConn, oTrans, oLogger, oVer):
    """Copy AbstractCard, upgrading as needed"""
    # pylint: disable-msg=E1101, R0912
    # E1101 - SQLObject confuses pylint
    # R0912 - need the branches for this
    aMessages = []
    if oVer.check_tables_and_versions([AbstractCard],
            [AbstractCard.tableversion], oOrigConn):
        copy_abstract_card(oOrigConn, oTrans, oLogger)
    elif oVer.check_tables_and_versions([AbstractCard], [5], oOrigConn):
        oTempConn = sqlhub.processConnection
        sqlhub.processConnection = oTrans
        sqlhub.processConnection = oTempConn
        for oCard in AbstractCard_v5.select(connection=oOrigConn):
            # force issue for SQObject >= 0.11.4
            oCard._connection = oOrigConn
            oCardCopy = AbstractCard(id=oCard.id,
                    canonicalName=oCard.canonicalName, name=oCard.name,
                    text=oCard.text, connection=oTrans)
            oCardCopy.group = oCard.group
            oCardCopy.capacity = oCard.capacity
            oCardCopy.cost = oCard.cost
            oCardCopy.costtype = oCard.costtype
            oCardCopy.level = oCard.level
            oCardCopy.life = oCard.life
            oCardCopy.search_text = strip_braces(oCard.text)
            for oData in oCard.rarity:
                oCardCopy.addRarityPair(oData)
            for oData in oCard.discipline:
                oCardCopy.addDisciplinePair(oData)
            for oData in oCard.rulings:
                oCardCopy.addRuling(oData)
            for oData in oCard.clan:
                oCardCopy.addClan(oData)
            for oData in oCard.cardtype:
                oCardCopy.addCardType(oData)
            for oData in oCard.sect:
                oCardCopy.addSect(oData)
            for oData in oCard.title:
                oCardCopy.addTitle(oData)
            for oData in oCard.creed:
                oCardCopy.addCreed(oData)
            for oData in oCard.virtue:
                oCardCopy.addVirtue(oData)
            for oData in oCard.keywords:
                oCardCopy.addKeyword(oData)
            for oData in oCard.artists:
                oCardCopy.addArtist(oData)
            oCardCopy.syncUpdate()
            oLogger.info('copied AC %s', oCardCopy.name)
    else:
        return (False, ["Unknown AbstractCard version"])
    return (True, aMessages)


def copy_physical_card(oOrigConn, oTrans, oLogger):
    """Copy PhysicalCard, assuming version match"""
    # We copy abstractCardID rather than abstractCard, to avoid issues
    # with abstract card class changes
    for oCard in PhysicalCard.select(connection=oOrigConn):
        oCardCopy = PhysicalCard(id=oCard.id,
                abstractCardID=oCard.abstractCardID,
                expansionID=oCard.expansionID, connection=oTrans)
        oLogger.info('copied PC %s', oCardCopy.id)


def copy_old_physical_card(oOrigConn, oTrans, oLogger, oVer):
    """Copy PhysicalCards, upgrading if needed."""
    aMessages = []
    if oVer.check_tables_and_versions([AbstractCard], [5], oOrigConn):
        for oCard in PhysicalCard_ACv5.select(connection=oOrigConn):
            oCardCopy = PhysicalCard(id=oCard.id,
                    abstractCardID=oCard.abstractCardID,
                    expansionID=oCard.expansionID, connection=oTrans)
            oCardCopy.syncUpdate()
            oLogger.info('copied PC %s', oCardCopy.id)
    elif oVer.check_tables_and_versions([PhysicalCard],
            [PhysicalCard.tableversion], oOrigConn):
        copy_physical_card(oOrigConn, oTrans, oLogger)
    else:
        return (False, ["Unknown PhysicalCard version"])
    return (True, aMessages)


def copy_physical_card_set(oOrigConn, oTrans, oLogger):
    """Copy PCS, assuming versions match"""
    aSets = list(PhysicalCardSet.select(connection=oOrigConn))
    copy_physical_card_set_loop(aSets, oTrans, oOrigConn, oLogger)


def copy_old_physical_card_set(oOrigConn, oTrans, oLogger, oVer):
    """Copy PCS, upgrading as needed."""
    # pylint: disable-msg=E1101, E1103
    # SQLObject confuses pylint
    aMessages = []
    if oVer.check_tables_and_versions([PhysicalCardSet],
            [PhysicalCardSet.tableversion], oOrigConn) \
            and oVer.check_tables_and_versions([PhysicalCard],
                    [PhysicalCard.tableversion], oOrigConn):
        copy_physical_card_set(oOrigConn, oTrans, oLogger)
    else:
        return (False, ["Unknown PhysicalCardSet version"])
    return (True, aMessages)


def read_old_database(oOrigConn, oDestConnn, oLogHandler=None):
    """Read the old database into new database, filling in
       blanks when needed"""
    # Magic happens in the individual functions, as needed
    aToCopy = [
            (copy_old_rarity, 'Rarity table', False),
            (copy_old_expansion, 'Expansion table', False),
            (copy_old_discipline, 'Discipline table', False),
            (copy_old_clan, 'Clan table', False),
            (copy_old_creed, 'Creed table', False),
            (copy_old_virtue, 'Virtue table', False),
            (copy_old_card_type, 'CardType table', False),
            (copy_old_ruling, 'Ruling table', False),
            (copy_old_discipline_pair, 'DisciplinePair table', False),
            (copy_old_rarity_pair, 'RarityPair table', False),
            (copy_old_sect, 'Sect table', False),
            (copy_old_title, 'Title table', False),
            (copy_old_artist, 'Artist table', False),
            (copy_old_keyword, 'Keyword table', False),
            (copy_old_abstract_card, 'AbstractCard table', True),
            (copy_old_physical_card, 'PhysicalCard table', True),
            (copy_old_physical_card_set, 'PhysicalCardSet table', True),
            ]
    iTotal = old_database_count(oOrigConn)
    return do_read_old_database(oOrigConn, oDestConnn, aToCopy, iTotal,
                                oLogHandler)

# pylint: enable-msg=W0612, C0103

# Not needed for 0.6 to 0.8 upgrade, but not deleting for future reference
#def drop_old_tables(_oConn):
#    """Drop tables which are no longer used from the database.
#       Needed for postgres and other such things."""


def copy_database(oOrigConn, oDestConnn, oLogHandler=None):
    """Copy the database, with no attempts to upgrade.

       This is a straight copy, with no provision for funky stuff
       Compatability of database structures is assumed, but not checked.
       """
    aToCopy = [
            (copy_rarity, 'Rarity table', False),
            (copy_expansion, 'Expansion table', False),
            (copy_discipline, 'Discipline table', False),
            (copy_clan, 'Clan table', False),
            (copy_creed, 'Creed table', False),
            (copy_virtue, 'Virtue table', False),
            (copy_card_type, 'CardType table', False),
            (copy_ruling, 'Ruling table', False),
            (copy_discipline_pair, 'DisciplinePair table', False),
            (copy_rarity_pair, 'RarityPair table', False),
            (copy_sect, 'Sect table', False),
            (copy_title, 'Title table', False),
            (copy_artist, 'Artist table', False),
            (copy_keyword, 'Keyword table', False),
            (copy_abstract_card, 'AbstractCard table', True),
            (copy_physical_card, 'PhysicalCard table', True),
            (copy_physical_card_set, 'PhysicalCardSet table', True),
            ]
    iTotal = new_database_count(oOrigConn)
    return do_copy_database(oOrigConn, oDestConnn, aToCopy, iTotal,
                            oLogHandler)


def create_memory_copy(oTempConn,  oLogHandler=None):
    return do_create_memory_copy(oTempConn, read_old_database)


def create_final_copy(oTempConn, oLogHandler=None):
    return do_create_final_copy(oTempConn, copy_database)


def attempt_database_upgrade(oLogHandler=None):
    return do_attempt_database_upgrade(create_memory_copy, create_final_copy,
                                oLogHandler)
