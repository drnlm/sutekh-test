# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Simon Cross <hodgestar@gmail.com>
# Copyright 2006 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details
# Misc Useful functions needed in several places. Mainly to do with database
# management. Seperated out from SutekhCli and other places, NM, 2006

"""Misc functions needed in various places in Sutekh."""

import tempfile
import os
import sys
import re
from sqlobject import sqlhub
import urlparse

from sutekh.core.Objects import VersionTable, flush_cache, CRYPT_TYPES, \
        PhysicalCardSet
from sutekh.core.generic.DatabaseVersion import DatabaseVersion
from sutekh.core.generic.DBUtilities import refresh_tables, get_cs_id_name_table
from sutekh.io.WhiteWolfTextParser import WhiteWolfTextParser
from sutekh.io.RulingParser import RulingParser
from sutekh.io.ExpDateCSVParser import ExpDateCSVParser

from sutekh.generic.Utility import (escape_quotes, unescape_quotes,
        gen_temp_file, gen_temp_dir, safe_filename, prefs_dir,
        ensure_dir_exists, sqlite_uri, pretty_xml, norm_xml_quotes,
        get_database_url, parse_string, write_string, move_articles_to_back,
        move_articles_to_front)


def read_white_wolf_list(aWwFiles, oLogHandler=None):
    """Parse in a new White Wolf cardlist

       aWwList is a list of objects with a .open() method (e.g.
       sutekh.io.WwFile.WwFile's)
       """
    flush_cache()
    oOldConn = sqlhub.processConnection
    sqlhub.processConnection = oOldConn.transaction()
    oParser = WhiteWolfTextParser(oLogHandler)
    for oFile in aWwFiles:
        fIn = oFile.open()
        oParser.parse(fIn)
        fIn.close()
    sqlhub.processConnection.commit(close=True)
    sqlhub.processConnection = oOldConn


def read_rulings(aRulings, oLogHandler=None):
    """Parse a new White Wolf rulings file

       oRulings is an object with a .open() method (e.g. a
       sutekh.io.WwFile.WwFile)
       """
    flush_cache()
    oOldConn = sqlhub.processConnection
    sqlhub.processConnection = oOldConn.transaction()
    oParser = RulingParser(oLogHandler)
    for oFile in aRulings:
        fIn = oFile.open()
        for sLine in fIn:
            oParser.feed(sLine)
        fIn.close()
    sqlhub.processConnection.commit(close=True)
    sqlhub.processConnection = oOldConn


def read_exp_date_list(aDateFiles, oLogHandler=None):
    flush_cache()
    oOldConn = sqlhub.processConnection
    sqlhub.processConnection = oOldConn.transaction()
    oParser = ExpDateCSVParser(oLogHandler)
    for oFile in aDateFiles:
        fIn = oFile.open()
        oParser.parse(fIn)
        fIn.close()
    sqlhub.processConnection.commit(close=True)
    sqlhub.processConnection = oOldConn


def format_text(sCardText):
    """Ensure card text is formatted properly"""
    # We want to split the . [dis] pattern into .\n[dis] again
    sResult = re.sub('(\.|\.\)) (\[...\])', '\\1\n\\2', sCardText)
    # But don't split the 'is not a discpline'
    return re.sub('\n(\[...\] is not a Dis)', ' \\1', sResult)


# Utility test for crypt cards
def is_crypt_card(oAbsCard):
    """Test if a card is a crypt card or not"""
    # Vampires and Imbued have exactly one card type (we hope that WW
    # don't change that)
    return oAbsCard.cardtype[0].name in CRYPT_TYPES


def is_vampire(oAbsCard):
    """Test if a card is a vampire or not"""
    return oAbsCard.cardtype[0].name == 'Vampire'


# Helper functions for the io routines
def monger_url(oCard, bVamp):
    """Return a monger url for the given AbstractCard"""
    sName = move_articles_to_back(oCard.name)
    if bVamp:
        if oCard.level is not None:
            sName = sName.replace(' (Advanced)', '')
            sMongerURL = "http://monger.vekn.org/showvamp.html?NAME=%s ADV" \
                    % sName
        else:
            sMongerURL = "http://monger.vekn.org/showvamp.html?NAME=%s" % sName
    else:
        sMongerURL = "http://monger.vekn.org/showcard.html?NAME=%s" % sName
    # May not need this, but play safe
    sMongerURL = sMongerURL.replace(' ', '%20')
    return sMongerURL


def secret_library_url(oCard, bVamp):
    """Return a Secret Library url for the given AbstractCard"""
    sName = move_articles_to_back(oCard.name)
    if bVamp:
        if oCard.level is not None:
            sName = sName.replace(' (Advanced)', '')
            sURL = "http://www.secretlibrary.info/?crypt=%s+Adv" \
                    % sName
        else:
            sURL = "http://www.secretlibrary.info/?crypt=%s" \
                    % sName
    else:
        sURL = "http://www.secretlibrary.info/?lib=%s" \
                    % sName
    sURL = sURL.replace(' ', '+')
    # ET will replace " with &quot;, which can lead to issues with SL, so we
    # drop double quotes entirely
    sURL = sURL.replace('"', '')
    return sURL
