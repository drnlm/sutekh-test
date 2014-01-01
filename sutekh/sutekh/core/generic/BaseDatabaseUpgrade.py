# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2013 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details
"""Generic components of the database upgrade.

   This provides some basic infrastructure for dealing with
   database upgrades, such as creating temporary databases and
   associated transactions. Most of the heavy grunt work isn't generic,
   so doesn't live here.
   """

# pylint: disable-msg=C0302
# This is a long module, partly because of the duplicated code from
# SutekhObjects. We want to keep all the database upgrade stuff together.
# so we jsut live with it

# pylint: disable-msg=E0611
# sqlobject confuses pylint here
from sqlobject import sqlhub, SQLObject, connectionForURI, SQLObjectNotFound
# pylint: enable-msg=E0611
from logging import Logger
from .CardSetHolder import CachedCardSetHolder
from .DBUtilities import refresh_tables
from .DatabaseVersion import DatabaseVersion
from .BaseObjects import PhysicalCardSet
from ..Objects import TABLE_LIST, flush_cache


# Utility Exception
class UnknownVersion(Exception):
    """Exception for versions we cannot handle"""
    def __init__(self, sTableName):
        Exception.__init__(self)
        self.sTableName = sTableName

    def __str__(self):
        return "Unrecognised version for %s" % self.sTableName


def copy_physical_card_set_loop(aSets, oTrans, oOrigConn, oLogger):
    """Central loop for copying card sets.

       Copy the list of card sets in aSet, ensuring we copy parents before
       children."""
    bDone = False
    dDone = {}
    # SQLObject < 0.11.4 does this automatically, but later versions don't
    # We depend on this, so we force the issue
    for oSet in aSets:
        oSet._connection = oOrigConn
    while not bDone:
        # We make sure we copy parent's before children
        # We need to be careful, since we don't retain card set IDs,
        # due to issues with sequence numbers
        aToDo = []
        for oSet in aSets:

            if oSet.parent is None or oSet.parent.id in dDone:
                if oSet.parent:
                    oParent = dDone[oSet.parent.id]
                else:
                    oParent = None
                # pylint: disable-msg=E1101
                # SQLObject confuses pylint
                oCopy = PhysicalCardSet(name=oSet.name,
                        author=oSet.author, comment=oSet.comment,
                        annotations=oSet.annotations, inuse=oSet.inuse,
                        parent=oParent, connection=oTrans)
                for oCard in oSet.cards:
                    oCopy.addPhysicalCard(oCard.id)
                oCopy.syncUpdate()
                oLogger.info('Copied PCS %s', oCopy.name)
                dDone[oSet.id] = oCopy
            else:
                aToDo.append(oSet)
        if not aToDo:
            bDone = True
        else:
            aSets = aToDo
        oTrans.commit()


def do_read_old_database(oOrigConn, oDestConnn, aToCopy, iTotal,
                         oLogHandler=None):
    """Read the old database into new database, filling in
       blanks when needed"""
    try:
        if not check_can_read_old_database(oOrigConn):
            return False
    except UnknownVersion, oExp:
        raise oExp
    oLogger = Logger('read Old DB')
    if oLogHandler:
        oLogger.addHandler(oLogHandler)
        if hasattr(oLogHandler, 'set_total'):
            oLogHandler.set_total(iTotal)
    # OK, version checks pass, so we should be able to deal with this
    aMessages = []
    bRes = True
    oTrans = oDestConnn.transaction()
    # Magic happens in the individual functions, as needed
    oVer = DatabaseVersion()
    for fCopy, sName, bPassLogger in aToCopy:
        try:
            if bPassLogger:
                (bOK, aNewMessages) = fCopy(oOrigConn, oTrans, oLogger, oVer)
            else:
                (bOK, aNewMessages) = fCopy(oOrigConn, oTrans, oVer)
        except SQLObjectNotFound, oExp:
            bOK = False
            aNewMessages = ['Unable to copy %s: Error %s' % (sName, oExp)]
        else:
            if not bPassLogger:
                oLogger.info('%s copied' % sName)
        bRes = bRes and bOK
        aMessages.extend(aNewMessages)
        oTrans.commit()
        oTrans.cache.clear()
    oTrans.commit(close=True)
    return (bRes, aMessages)

# pylint: enable-msg=W0612, C0103


def do_copy_database(oOrigConn, oDestConnn, aToCopy, iTotal,
                     oLogHandler=None):
    """Copy the database, with no attempts to upgrade.

       This is a straight copy, with no provision for funky stuff
       Compatability of database structures is assumed, but not checked.
       """
    # Not checking versions probably should be fixed
    # Copy tables needed before we can copy AbstractCard
    flush_cache()
    oVer = DatabaseVersion()
    oVer.expire_cache()
    oLogger = Logger('copy DB')
    if oLogHandler:
        oLogger.addHandler(oLogHandler)
        if hasattr(oLogHandler, 'set_total'):
            oLogHandler.set_total(iTotal)
    bRes = True
    aMessages = []
    oTrans = oDestConnn.transaction()
    for fCopy, sName, bPassLogger in aToCopy:
        try:
            if bRes:
                if bPassLogger:
                    fCopy(oOrigConn, oTrans, oLogger)
                else:
                    fCopy(oOrigConn, oTrans)
        except SQLObjectNotFound, oExp:
            bRes = False
            aMessages.append('Unable to copy %s: Aborting with error: %s'
                    % (sName, oExp))
        else:
            oTrans.commit()
            oTrans.cache.clear()
            if not bPassLogger:
                oLogger.info('%s copied' % sName)
    flush_cache()
    oTrans.commit(close=True)
    # Clear out cache related joins and such
    return bRes, aMessages


def make_card_set_holder(oCardSet, oOrigConn):
    """Given a CardSet, create a Cached Card Set Holder for it."""
    oCurConn = sqlhub.processConnection
    sqlhub.processConnection = oOrigConn
    oCS = CachedCardSetHolder()
    oCS.name = oCardSet.name
    oCS.author = oCardSet.author
    oCS.comment = oCardSet.comment
    oCS.annotations = oCardSet.annotations
    oCS.inuse = oCardSet.inuse
    if oCardSet.parent:
        oCS.parent = oCardSet.parent.name
    for oCard in oCardSet.cards:
        if oCard.expansion is None:
            oCS.add(1, oCard.abstractCard.canonicalName, None)
        else:
            oCS.add(1, oCard.abstractCard.canonicalName, oCard.expansion.name)
    sqlhub.processConnection = oCurConn
    return oCS


def copy_to_new_abstract_card_db(oOrigConn, oNewConn, oCardLookup,
        oLogHandler=None):
    """Copy the card sets to a new Physical Card and Abstract Card List.

      Given an existing database, and a new database created from
      a new cardlist, copy the CardSets, going via CardSetHolders, so we
      can adapt to changed names, etc.
      """
    # pylint: disable-msg=R0914
    # we need a lot of variables here
    aPhysCardSets = []
    oOldConn = sqlhub.processConnection
    sqlhub.processConnection = oOrigConn
    # Copy Physical card sets
    oLogger = Logger('copy to new abstract card DB')
    if oLogHandler:
        oLogger.addHandler(oLogHandler)
        if hasattr(oLogHandler, 'set_total'):
            iTotal = 1 + PhysicalCardSet.select(connection=oOrigConn).count()
            oLogHandler.set_total(iTotal)
    aSets = list(PhysicalCardSet.select(connection=oOrigConn))
    bDone = False
    aDone = []
    # Ensre we only process a set after it's parent
    while not bDone:
        aToDo = []
        for oSet in aSets:
            if oSet.parent is None or oSet.parent in aDone:
                oCS = make_card_set_holder(oSet, oOrigConn)
                aPhysCardSets.append(oCS)
                aDone.append(oSet)
            else:
                aToDo.append(oSet)
        if not aToDo:
            bDone = True
        else:
            aSets = aToDo
    # Save the current mapping
    oLogger.info('Memory copies made')
    # Create the cardsets from the holders
    dLookupCache = {}
    sqlhub.processConnection = oNewConn
    for oSet in aPhysCardSets:
        # create_pcs will manage transactions for us
        oSet.create_pcs(oCardLookup, dLookupCache)
        oLogger.info('Physical Card Set: %s', oSet.name)
        sqlhub.processConnection.cache.clear()
    sqlhub.processConnection = oOldConn
    return (True, [])


def do_create_memory_copy(oTempConn, fReadOldCopy, oLogHandler=None):
    """Create a temporary copy of the database in memory.

      We create a temporary memory database, and create the updated
      database in it. readOldDB is responsbile for upgrading stuff
      as needed
      """
    if refresh_tables(TABLE_LIST, oTempConn, False):
        bRes, aMessages = fReadOldCopy(sqlhub.processConnection,
                oTempConn, oLogHandler)
        oVer = DatabaseVersion()
        oVer.expire_cache()
        return bRes, aMessages
    return (False, ["Unable to create tables"])


def do_create_final_copy(oTempConn, fCopy, oLogHandler=None):
    """Copy from the memory database to the real thing"""
    #drop_old_tables(sqlhub.processConnection)
    if refresh_tables(TABLE_LIST, sqlhub.processConnection):
        return fCopy(oTempConn, sqlhub.processConnection, oLogHandler)
    return (False, ["Unable to create tables"])


def do_attempt_database_upgrade(fMemory, fFinal, oLogHandler=None):
    """Attempt to upgrade the database, going via a temporary memory copy."""
    oTempConn = connectionForURI("sqlite:///:memory:")
    oLogger = Logger('attempt upgrade')
    if oLogHandler:
        oLogger.addHandler(oLogHandler)
    (bOK, aMessages) = fMemory(oTempConn, oLogHandler)
    if bOK:
        oLogger.info("Copied database to memory, performing upgrade.")
        if len(aMessages) > 0:
            oLogger.info("Messages reported: %s", aMessages)
        (bOK, aMessages) = fFinal(oTempConn, oLogHandler)
        if bOK:
            oLogger.info("Everything seems to have gone OK")
            if len(aMessages) > 0:
                oLogger.info("Messages reported %s", aMessages)
            return True
        else:
            oLogger.critical("Unable to perform upgrade.")
            if len(aMessages) > 0:
                oLogger.error("Errors reported: %s", aMessages)
            oLogger.critical("!!YOUR DATABASE MAY BE CORRUPTED!!")
    else:
        oLogger.error("Unable to create memory copy. Database not upgraded.")
        if len(aMessages) > 0:
            oLogger.error("Errors reported %s", aMessages)
    return False
