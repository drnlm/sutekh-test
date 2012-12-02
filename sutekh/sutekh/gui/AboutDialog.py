# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2007 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Simple about dialog for Sutekh"""

from sutekh.gui import SutekhIcon
from sutekh.SutekhInfo import SutekhInfo
import gtk

from sqlobject import sqlhub
import urlparse


# pylint: disable-msg=R0904
# R0904 - gtk Widget, so has many public methods
class SutekhAboutDialog(gtk.AboutDialog):
    """About dialog for Sutekh."""

    # pylint: disable-msg=W0142
    # ** magic OK here
    def __init__(self, *aArgs, **kwargs):
        super(SutekhAboutDialog, self).__init__(*aArgs, **kwargs)

        self.set_name(SutekhInfo.NAME)
        self.set_version(SutekhInfo.VERSION_STR)
        self.set_copyright(SutekhInfo.LICENSE)
        self.set_comments(SutekhInfo.DESCRIPTION)
        self.set_license(SutekhInfo.LICENSE_TEXT)
        self.set_wrap_license(False)  # don't automatically wrap license text
        self.set_website(SutekhInfo.SOURCEFORGE_URL)
        self.set_website_label("Website")
        self.set_authors([tAuth[0] for tAuth in SutekhInfo.AUTHORS])
        self.set_documenters([tAuth[0] for tAuth in SutekhInfo.DOCUMENTERS])
        self.set_artists([tAuth[0] for tAuth in SutekhInfo.ARTISTS])
        self.set_logo(SutekhIcon.SUTEKH_ICON)
        # self.set_translator_credits(translator_credits)

        sDBuri = sqlhub.processConnection.uri()
        # pylint: disable-msg=E1103, E1101
        # pylint doesn't like the SpiltResult named tuple and the dialog
        # vbox
        tParsed = urlparse.urlsplit(sDBuri)
        if tParsed.password:
            tCombined = (tParsed.scheme,
                    tParsed.netloc.replace(tParsed.password, '****'),
                    tParsed.path, tParsed.query, tParsed.fragment)
            sUrl = urlparse.urlunsplit(tCombined)
        else:
            sUrl = sDBuri

        oUrlText = gtk.Label('Database URI: %s' % sUrl)
        self.vbox.pack_end(oUrlText, False, False)
        oUrlText.show()
