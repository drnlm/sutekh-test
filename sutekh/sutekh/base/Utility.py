# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Simon Cross <hodgestar@gmail.com>
# Copyright 2006 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details
# Misc Useful functions needed in several places. Mainly to do with database
# management. Seperated out from SutekhCli and other places, NM, 2006

"""Misc functions that have no internal dependancies and can be imported into
   core."""

import tempfile
import os
import sys
from sqlobject import sqlhub
from StringIO import StringIO
import urlparse

# Helper functions for dealing with strings
def escape_quotes(sData):
    """Escape quotes and \\'s in the string"""
    # escape \'s
    sResult = sData.replace('\\', '\\\\')
    # escape quotes
    sResult = sResult.replace("'", "\\'")
    sResult = sResult.replace('"', '\\"')
    return sResult


def unescape_quotes(sData):
    """Unescape quotes and \\'s in the string.

       should be the inverse of escape_quotes."""
    # unescape quotes
    # We assume that this is called on a escaped sring, after any
    # surrounding quotes have been stripped off, so there are no unescaped
    # quotes to worry about
    sResult = sData.replace("\\'", "'")
    sResult = sResult.replace('\\"', '"')
    # unsecape \\
    sResult = sResult.replace('\\\\', '\\')
    return sResult


def gen_temp_file(sBaseName, sDir):
    """Simple wrapper around tempfile creation - generates the name and closes
       the file
       """
    (fTemp, sFilename) = tempfile.mkstemp('.xml', sBaseName, sDir)
    # This may not be nessecary, but the available documentation
    # suggests that, on Windows NT anyway, leaving the file open will
    # cause problems if we try to reopen it
    os.close(fTemp)
    # There is a race condition here, but since Sutekh should not be running
    # with elevated priveleges, this should never be a security issues
    # The race requires something to delete and replace the tempfile,
    # I don't see it being triggered accidently
    return sFilename


def gen_temp_dir():
    """Create a temporary directory using mkdtemp"""
    sTempdir = tempfile.mkdtemp('dir', 'sutekh')
    return sTempdir


def safe_filename(sFilename):
    """Replace potentially dangerous and annoying characters in the name -
       used to automatically generate sensible filenames from card set names
       """
    sSafeName = sFilename
    sSafeName = sSafeName.replace(" ", "_")  # I dislike spaces in filenames
    # Prevented unexpected filesystem issues
    sSafeName = sSafeName.replace("/", "_")
    sSafeName = sSafeName.replace("\\", "_")  # ditto for windows
    return sSafeName


def prefs_dir(sApp):
    """Return a suitable directory for storing preferences and other
       application data."""
    if sys.platform.startswith("win") and "APPDATA" in os.environ:
        return os.path.join(os.environ["APPDATA"], sApp)
    else:
        return os.path.join(os.path.expanduser("~"), ".%s" % sApp.lower())


def ensure_dir_exists(sDir):
    """Check that a directory exists and create it if it doesn't.
       """
    if os.path.exists(sDir):
        assert os.path.isdir(sDir)
    else:
        os.makedirs(sDir)


def sqlite_uri(sPath):
    """Create an SQLite db URI from the path to the db file.
       """
    sDbFile = sPath.replace(os.sep, "/")

    sDrive, sRest = os.path.splitdrive(sDbFile)
    if sDrive:
        sDbFile = "/" + sDrive.rstrip(':') + "|" + sRest
    else:
        sDbFile = sRest

    return "sqlite://" + sDbFile


def pretty_xml(oElement, iIndentLevel=0):
    """
    Helper function to add whitespace text attributes to a ElementTree.
    Makes for 'pretty' indented XML output.
    Based on the example indent function at
    http://effbot.org/zone/element-lib.htm [22/01/2008]
    """
    sIndent = "\n" + iIndentLevel * "  "
    if len(oElement):
        if not oElement.text or not oElement.text.strip():
            oElement.text = sIndent + "  "
            for oSubElement in oElement:
                pretty_xml(oSubElement, iIndentLevel + 1)
            # Reset indentation level for last child element
            # pylint: disable-msg=W0631
            # We know SubElement will exist because of the len check above
            if not oSubElement.tail or not oSubElement.tail.strip():
                oSubElement.tail = sIndent
    else:
        if iIndentLevel and (not oElement.tail or not oElement.tail.strip()):
            oElement.tail = sIndent


def norm_xml_quotes(sData):
    """Normalise quote escaping from ElementTree, to hide version
       differences"""
    # Because of how ElementTree adds quotes internally, this should always
    # be safe
    return sData.replace('&apos;', "'")


def get_database_url():
    """Return the database url, with the password stripped out if
       needed"""
    sDBuri = sqlhub.processConnection.uri()
    # pylint: disable-msg=E1103
    # pylint doesn't like the SpiltResult named tuple
    tParsed = urlparse.urlsplit(sDBuri)
    if tParsed.password:
        tCombined = (tParsed.scheme,
                tParsed.netloc.replace(tParsed.password, '****'),
                tParsed.path, tParsed.query, tParsed.fragment)
        sUrl = urlparse.urlunsplit(tCombined)
    else:
        sUrl = sDBuri
    return sUrl


# Helper's for io modules
def parse_string(oParser, sIn, oHolder):
    """Utitlity function.
       Allows oParser.parse to be called on a string."""
    oFile = StringIO(sIn)
    oParser.parse(oFile, oHolder)


def write_string(oWriter, oHolder):
    """Utility function.
       Generate a string from the Writer."""
    oFile = StringIO()
    oWriter.write(oFile, oHolder)
    oString = oFile.getvalue()
    oFile.close()
    return oString


def move_articles_to_back(sName):
    """Moves articles to the end of the name"""
    if sName.startswith('The '):
        sName = sName[4:] + ", The"
    elif sName.startswith('An '):
        sName = sName[3:] + ", An"
    elif sName.startswith('A '):
        sName = sName[2:] + ", A"
    return sName


def move_articles_to_front(sName):
    """Move articles at the end to the front.

       Reverses move_articles_to_back"""
       # handle case variations as well
    if sName.lower().endswith(', the'):
        sName = "The " + sName[:-5]
    elif sName.lower().endswith(', an'):
        sName = "An " + sName[:-4]
    elif sName.lower().endswith(', a'):
        sName = "A " + sName[:-3]
    # The result might be mixed case, but, as we should feed this into
    # IAbstractCard in most cases, that won't matter
    return sName
