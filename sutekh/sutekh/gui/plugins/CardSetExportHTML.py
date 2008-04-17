# CardSetExportHTML.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2007 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Export a card set to HTML."""

import gtk
import time
from sutekh.core.SutekhObjects import PhysicalCardSet, AbstractCardSet, \
        IAbstractCard
from sutekh.gui.PluginManager import CardListPlugin
from sutekh.gui.SutekhDialog import do_complaint_error
from sutekh.gui.SutekhFileWidget import ExportDialog
from sutekh.core.ArdbInfo import ArdbInfo
from sutekh.SutekhInfo import SutekhInfo
from sutekh.SutekhUtility import pretty_xml, safe_filename
# pylint: disable-msg=F0401, E0611
# the allowe failures here makes pylint unhappy
try:
    from xml.etree.ElementTree import ElementTree, Element, SubElement
except ImportError:
    from elementtree.ElementTree import ElementTree, Element, SubElement
# pylint: enable-msg=F0401, E0611

# Style used by the HTML file
_sHTMLStyle = """
body {
   background: #000000;
   color: #AAAAAA;
   margin: 0
}

div#crypt { background: #000000; }

div#info {
   background: #331111;
   width: 100%;
}

div#library {
   background: #000000
   url("http://www.white-wolf.com/VTES/images/CardsImg.jpg")
   no-repeat scroll top right;
}

h1 {
   font-size: x-large;
   margin-left: 1cm
}

h2 {
   font-size: large;
   margin-left: 1cm
}

h3 {
   font-size: large;
   border-bottom: solid;
   border-width: 2px;
}

h4 {
   font-size: medium;
   margin-bottom: 0px
}

div#cardtext { background: #000000 }

div#cardtext h4 { text-decoration: underline; }

div#cardtext h5 {
   font-weight: normal;
   text-decoration: underline;
   margin-left: 1em;
   margin-bottom: 0.1em;
}

div#cardtext div.text { margin-left: 1em; }

div#cardtext ul {
   list-style-type: none;
   margin-top: 0.1em;
   margin-bottom: 0.1em;
   padding-left: 1em;
}

div#cardtext .label { font-style: italic; }

div#cardtext p {
   margin-left: 0.3em;
   margin-bottom: 0.1em;
   margin-top: 0em;
}

table { line-height: 70% }

.generator {
   color: #555555;
   position: relative;
   top: 20px;
}

.librarytype { }

.stats {
   color: #777777;
   margin: 5px;
}

.tablevalue {
    color: #aaaa88;
    margin: 5px
}

.value { color: #aaaa88 }

hr { color: sienna }

p { margin-left: 60px }

a {
    color: #aaaa88;
    margin: 5px;
    text-decoration: none
}

a:hover {
    color: #ffffff;
    margin: 5px;
    text-decoration: none
}
"""

def _monger_url(oCard, bVamp):
    """Return a monger url for the given AbstractCard"""
    sName = oCard.name
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

def _sort_vampires(dVamps):
    """Sort the vampires by number, then capacity."""
    aSortedVampires = []
    # pylint: disable-msg=E1101
    # IAbstrctCard confuses pylint
    for iId, sVampName in dVamps:
        oCard = IAbstractCard(sVampName)
        iCount = dVamps[(iId, sVampName)]
        if len(oCard.creed) > 0:
            iCapacity = oCard.life
            sClan = "Imbued"
        else:
            iCapacity = oCard.capacity
            sClan = [oClan.name for oClan in oCard.clan][0]
        aSortedVampires.append(((iCount, iCapacity, sVampName, sClan), oCard))
    # We reverse sort by Capacity and Count, normal sort by name
    # fortunately, python's sort is stable, so this works
    aSortedVampires.sort(key=lambda x: x[0][2])
    aSortedVampires.sort(key=lambda x: (x[0][0], x[0][1]), reverse=True)
    # This doesn't get the same ordering for advanced vampires as
    # the XSLT approach, but I don't care enough to tweak that
    return aSortedVampires

def _sort_lib(dLib):
    """Extract a list of cards sorted into types from the library"""
    dTypes = {}
    # Group by type
    for tKey in dLib:
        # pylint: disable-msg=W0612
        # iId isn't used here
        iId, sName, sType = tKey
        iCount = dLib[tKey]
        dTypes.setdefault(sType, [0])
        dTypes[sType][0] += iCount
        dTypes[sType].append((iCount, sName))
    return sorted(dTypes.items())

def _add_span(oElement, sText, sClass=None, sId=None):
    """Add a span element to the element oElement"""
    oSpan = SubElement(oElement, "span")
    oSpan.text = sText
    if sClass:
        oSpan.attrib['class'] = sClass
    if sId:
        oSpan.attrib['id'] = sId

def _add_text(oElement, oCard):
    """Add the card text to the ElementTree line by line"""
    oTextDiv = SubElement(oElement, "div")
    oTextDiv.attrib["class"] = "text"
    for sLine in oCard.text.splitlines():
        oPara = SubElement(oTextDiv, 'p')
        oPara.text = sLine

class CardSetExportHTML(CardListPlugin, ArdbInfo):
    """Export a Card set to a 'nice' HTML file.

       We create a ElementTree that represents the XHTML file,
       and then dump that to file.
       This tries to match the HTML file produced by ARDB.
       """
    dTableVersions = { AbstractCardSet: [2, 3],
                       PhysicalCardSet: [2, 3, 4]}
    aModelsSupported = [AbstractCardSet, PhysicalCardSet]

    # HTML style definition
    def get_menu_item(self):
        """Register on the Plugins Menu"""
        if not self.check_versions() or not self.check_model_type():
            return None

        oExport = gtk.MenuItem("Export Card Set to HTML")
        oExport.connect("activate", self.activate)
        return ('Plugins', oExport)

    # pylint: disable-msg=W0613
    # oWidget required by function signature
    def activate(self, oWidget):
        """In response to the menu, create the dialog and run it."""
        oDlg = self.make_dialog()
        oDlg.run()
        self.handle_response(oDlg.get_name())

    # pylint: enable-msg=W0613

    # pylint: disable-msg=W0201
    # we define attributes outside __init__, but it's OK because of plugin
    # structure
    def make_dialog(self):
        """Create the dialog prompted for the filename."""
        oDlg = ExportDialog("Filename to save as", self.parent,
                '%s.html' % safe_filename(self.view.sSetName))
        # pylint: disable-msg=E1101
        # vbox confuses pylint
        self.oTextButton = gtk.CheckButton("Include Card _Texts?")
        self.oTextButton.set_active(False)
        oDlg.vbox.pack_start(self.oTextButton, False, False)
        oDlg.show_all()
        return oDlg

    # pylint: enable-msg=W0201

    def handle_response(self, sFileName):
        """Handle the response to the dialog"""
        # pylint: disable-msg=E1101
        # SQLObject methods confuse pylint
        if sFileName is not None:
            # pylint: disable-msg=W0703
            # we do want to catch all exceptions here
            try:
                fOut = file(sFileName, "w")
            except Exception, oExp:
                sMsg = "Failed to open output file.\n\n" + str(oExp)
                do_complaint_error(sMsg)
                return
            oCardSet = self.get_card_set()
            if not oCardSet:
                fOut.close()
                do_complaint_error("Unsupported Card Set Type")
                return
            bDoText = False
            if self.oTextButton.get_active():
                bDoText = True
            oETree = self.gen_tree(oCardSet, bDoText)
            # We're producing XHTML output, so we need a doctype header
            fOut.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0'
                    ' Strict//EN"\n "http://www.w3.org/TR/xhtml1/DTD/'
                    'xhtml1-strict.dtd">\n')
            # We have the elementree with the needed information,
            # need to produce decent HTML output
            oETree.write(fOut)
            fOut.close()

    def get_cards(self):
        """Get the cards for this card set."""
        # pylint: disable-msg=E1101
        # PyProtocol methods confuse pylint
        dDict = {}
        for oCard in self.model.get_card_iterator(None):
            oACard = IAbstractCard(oCard)
            dDict.setdefault((oACard.id, oACard.name), 0)
            dDict[(oACard.id, oACard.name)] += 1
        return dDict

    def gen_tree(self, oCardSet, bDoText):
        """Convert the Cards to a element tree containing 'nice' HTML"""
        oDocRoot = Element('html', xmlns='http://www.w3.org/1999/xhtml',
                lang='en')
        oDocRoot.attrib["xml:lang"] = 'en'

        oBody = self._add_header(oDocRoot, oCardSet)

        dCards = self.get_cards()
        aSortedVampires = self._add_crypt(oBody, dCards)
        aSortedLibCards = self._add_library(oBody, dCards)
        if bDoText:
            oCardText = SubElement(oBody, "div", id="cardtext")
            oTextHead = SubElement(oCardText, "h3")
            oTextHead.attrib["class"] = "cardtext"
            _add_span(oTextHead, 'Card Texts')
            self._add_crypt_text(oCardText, aSortedVampires)
            self._add_library_text(oCardText, aSortedLibCards)

        # Closing stuff
        oGenerator = SubElement(oBody, "div")
        _add_span(oGenerator, "Crafted with : Sutekh [ %s ]. [ %s ]" %
                (SutekhInfo.VERSION_STR,
                    time.strftime('%Y-%m-%d', time.localtime())),
                "generator")

        pretty_xml(oDocRoot)
        return ElementTree(oDocRoot)

    # methods to fill in the actual HTML content
    # pylint: disable-msg=R0201
    # these are all methods for consistency
    def _add_header(self, oDocRoot, oCardSet):
        """Add the header and title of the HTML file."""
        oHead = SubElement(oDocRoot, 'head')
        oStyle = SubElement(oHead, 'style', type="text/css")
        # Is there a better idea here?
        oStyle.text = _sHTMLStyle
        oTitle = SubElement(oHead, "title")
        oTitle.text = "VTES deck : %s by %s" % (oCardSet.name,
                oCardSet.author)

        oBody = SubElement(oDocRoot, "body")
        oInfo = SubElement(oBody, "div", id="info")
        oName = SubElement(oInfo, "h1", id="nametitle")
        _add_span(oName, 'Deck Name :')
        _add_span(oName, oCardSet.name, 'value', 'namevalue')
        oAuthor = SubElement(oInfo, "h2", id="authortitle")
        _add_span(oAuthor, 'Author : ')
        _add_span(oAuthor, oCardSet.author, 'value', 'authornamevalue')
        oDesc = SubElement(oInfo, "h2", id="description")
        _add_span(oDesc, 'Description : ')
        oPara = SubElement(oInfo, "p")
        _add_span(oPara, oCardSet.comment, 'value', 'descriptionvalue')
        return oBody

    def _add_crypt(self, oBody, dCards):
        """Add the crypt to the file"""
        # pylint: disable-msg=E1101
        # PyProtocol methods confuse pylint
        def start_section(oBody, dCards):
            """Format the start of the crypt section"""
            (dVamps, iCryptSize, iMin, iMax, fAvg) = self._extract_crypt(
                    dCards)
            oCrypt = SubElement(oBody, "div", id="crypt")
            oCryptTitle = SubElement(oCrypt, "h3", id="crypttitle")
            _add_span(oCryptTitle, 'Crypt')
            _add_span(oCryptTitle, "[%d vampires] Capacity min : %d max :"
                    " %d average : %.2f" % (iCryptSize, iMin, iMax, fAvg),
                    'stats', 'cryptstats')
            aSortedVampires = _sort_vampires(dVamps)
            return oCrypt, aSortedVampires

        def add_row(oCryptTBody, tVampInfo, oCard):
            """Add a row to the display table"""
            oTR = SubElement(oCryptTBody, "tr")
            # Card Count
            oTD = SubElement(oTR, "td")
            _add_span(oTD, "%dx" % tVampInfo[0], 'tablevalue')
            # Card Name + Monger href
            oTD = SubElement(oTR, "td")
            oSpan = SubElement(oTD, "span")
            oSpan.attrib["class"] = "tablevalue"
            # May be able to get away without this, but being safe
            oMongerHREF = SubElement(oSpan, "a", href=_monger_url(oCard, True))
            oMongerHREF.text = tVampInfo[2].replace(' (Advanced)', '')
            oTD = SubElement(oTR, "td")
            # Advanced status
            if oCard.level is not None:
                _add_span(oTD, '(Advanced)', 'tablevalue')
            # Capacity
            oTD = SubElement(oTR, "td")
            _add_span(oTD, str(tVampInfo[1]), 'tablevalue')
            # Disciplines
            oTD = SubElement(oTR, "td")
            _add_span(oTD, self._gen_disciplines(oCard), 'tablevalue')
            # Title
            oTD = SubElement(oTR, "td")
            if len(oCard.title) > 0:
                _add_span(oTD, [oTitle.name for oTitle in oCard.title][0],
                        'tablevalue')
            # Clan
            oTD = SubElement(oTR, "td")
            _add_span(oTD, "%s (group %d)" % (tVampInfo[3], oCard.group),
                    'tablevalue')

        oCrypt, aSortedVampires = start_section(oBody, dCards)
        oCryptTBody = SubElement(
                SubElement(
                    SubElement(oCrypt, "div", id="crypttable"),
                    "table", summary="Crypt card table"),
                "tbody")
        # Need to sort vampires by number, then capacity
        for tVampInfo, oCard in aSortedVampires:
            add_row(oCryptTBody, tVampInfo, oCard)
        return aSortedVampires

    def _add_library(self, oBody, dCards):
        """Add the library cards to the tree"""
        def start_section(oBody, dCards):
            """Set up the header for this section"""
            (dLib, iLibSize) = self._extract_library(dCards)
            aSortedLibCards = _sort_lib(dLib)
            oLib = SubElement(oBody, "div", id="library")
            oLibTitle = SubElement(oLib, "h3", id="librarytitle")
            _add_span(oLibTitle, "Library")
            _add_span(oLibTitle, '[%d cards]' % iLibSize, 'stats',
                    'librarystats')
            return oLib, aSortedLibCards

        def add_row(oTBody, iCount, sName):
            """Add a row to the display table"""
            # pylint: disable-msg=E1101
            # IAbstrctCard confuses pylint
            oCard = IAbstractCard(sName)
            oTR = SubElement(oTBody, "tr")
            oTD = SubElement(oTR, "td")
            _add_span(oTD, '%dx' % iCount, 'tablevalue')
            oTD = SubElement(oTR, "td")
            oSpan = SubElement(oTD, "span")
            oSpan.attrib["class"] = "tablevalue"
            oMongerHRef = SubElement(oSpan, "a", href=_monger_url(oCard,
                False))
            oMongerHRef.text = sName

        oLib, aSortedLibCards = start_section(oBody, dCards)
        oLibTable = SubElement(oLib, "div")
        oLibTable.attrib["class"] = "librarytable"

        for sType, aList in aSortedLibCards:
            oTypeHead = SubElement(oLibTable, "h4")
            oTypeHead.attrib["class"] = "librarytype"
            _add_span(oTypeHead, sType)
            _add_span(oTypeHead, '[%d]' % aList[0], 'stats')
            oTBody = SubElement(
                    SubElement(oLibTable, "table",
                        summary="Library card table"),
                    "tbody")
            # Sort alphabetically within cards
            for iCount, sName in sorted(aList[1:], key=lambda x: x[1]):
                add_row(oTBody, iCount, sName)
        return aSortedLibCards

    def _add_crypt_text(self, oCardText, aSortedVampires):
        """Add the text of the crypt to the element tree"""
        oCryptTextHead = SubElement(oCardText, "h4")
        oCryptTextHead.attrib["class"] = "librarytype"
        oCryptTextHead.text = "Crypt"
        for tVampInfo, oCard in aSortedVampires:
            oCardName = SubElement(oCardText, "h5")
            oCardName.text = tVampInfo[2]
            oList = SubElement(oCardText, "ul")
            # Capacity
            oListItem = SubElement(oList, "li")
            _add_span(oListItem, 'Capacity:', 'label')
            _add_span(oListItem, str(tVampInfo[1]), 'capacity')
            # Group
            oListItem = SubElement(oList, "li")
            _add_span(oListItem, 'Group:', 'label')
            _add_span(oListItem, str(oCard.group), 'group')
            # Clan
            oListItem = SubElement(oList, "li")
            _add_span(oListItem, 'Clan:', 'label')
            _add_span(oListItem, tVampInfo[3], 'clan')
            # Disciplines
            oListItem = SubElement(oList, "li")
            _add_span(oListItem, 'Disciplines:', 'label')
            _add_span(oListItem, self._gen_disciplines(oCard), 'disciplines')
            # Text
            _add_text(oCardText, oCard)

    def _add_library_text(self, oCardText, aSortedLibCards):
        """Add the text of the library cards to the tree."""
        def gen_requirements(oCard):
            """Extract the requirements from the card"""
            oList = Element("ul")
            # Clan requirements
            aClan = [x.name for x in oCard.clan]
            if len(aClan) > 0:
                oListItem = SubElement(oList, "li")
                _add_span(oListItem, 'Requires:', 'label')
                _add_span(oListItem, "/".join(aClan), 'requirement')
            # Cost
            if oCard.costtype is not None:
                # pylint: disable-msg=E1103
                # SQLObject methods confuse pylint
                oListItem = SubElement(oList, "li")
                _add_span(oListItem, 'Cost:', 'label')
                _add_span(oListItem, "%d %s" % (oCard.cost,
                    oCard.costtype), 'cost')
            # Disciplines
            sDisciplines = self._gen_disciplines(oCard)
            if sDisciplines != "":
                oListItem = SubElement(oList, "li")
                _add_span(oListItem, 'Disciplines:', 'label')
                _add_span(oListItem, sDisciplines, 'disciplines')
            return oList

        for sType, aList in aSortedLibCards:
            oTypeHead = SubElement(oCardText, "h4")
            oTypeHead.attrib["class"] = "libraryttype"
            oTypeHead.text = sType
            for sName in sorted([x[1] for x in aList[1:]]):
                # pylint: disable-msg=E1101
                # IAbstrctCard confuses pylint
                oCard = IAbstractCard(sName)
                oCardHead = SubElement(oCardText, "h5")
                oCardHead.attrib["class"] = "cardname"
                oCardHead.text = sName
                oList = gen_requirements(oCard)
                if len(oList) > 0:
                    # not empty, so add
                    oCardText.append(oList)
                # Text
                _add_text(oCardText, oCard)

# pylint: disable-msg=C0103
# accept plugin name
plugin = CardSetExportHTML
