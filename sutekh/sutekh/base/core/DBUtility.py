# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Simon Cross <hodgestar@gmail.com>
# Copyright 2006 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details
# Misc Useful functions needed in several places. Mainly to do with database
# management. Seperated out from SutekhCli and other places, NM, 2006

"""Misc functions needed in various places in Sutekh."""


from .BaseObjects import VersionTable, PhysicalCardSet
from sutekh.core.SutekhObjects import flush_cache
from .DatabaseVersion import DatabaseVersion


def refresh_tables(aTables, oConn, bMakeCache=True):
    """Drop and recreate the given list of tables"""
    aTables.reverse()
    for cCls in aTables:
        cCls.dropTable(ifExists=True, connection=oConn)
    aTables.reverse()
    oVerHandler = DatabaseVersion(oConn)
    # Make sure we recreate the database version table
    oVerHandler.expire_table_conn(oConn)
    oVerHandler.ensure_table_exists(oConn)
    if not oVerHandler.set_version(VersionTable, VersionTable.tableversion,
            oConn):
        return False
    for cCls in aTables:
        cCls.createTable(connection=oConn)
        if not oVerHandler.set_version(cCls, cCls.tableversion, oConn):
            return False
    flush_cache(bMakeCache)
    return True


# Utility function to help with config management and such
def get_cs_id_name_table():
    """Returns a dictionary id : name for all the card sets.

       We do this so we can have the old info available to fix the config
       after a database reload, etc."""
    dMapping = {}
    for oCS in PhysicalCardSet.select():
        dMapping[oCS.id] = oCS.name
    return dMapping
