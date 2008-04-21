# test_CardSets.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Test Card Set handling"""

from sutekh.tests.TestCore import SutekhTest
from sutekh.core.SutekhObjects import IAbstractCard, PhysicalCard, \
        IExpansion, PhysicalCardSet, AbstractCardSet, IPhysicalCardSet, \
        IAbstractCardSet, MapPhysicalCardToPhysicalCardSet, \
        MapAbstractCardToAbstractCardSet
from sutekh.io.PhysicalCardSetParser import PhysicalCardSetParser
from sutekh.io.PhysicalCardSetWriter import PhysicalCardSetWriter
from sutekh.io.AbstractCardSetParser import AbstractCardSetParser
from sutekh.io.AbstractCardSetWriter import AbstractCardSetWriter
from sutekh.io.IdentifyXMLFile import IdentifyXMLFile
from sutekh.SutekhUtility import delete_physical_card_set, \
        delete_abstract_card_set
from sqlobject import SQLObjectNotFound
import unittest

class PhysicalCardSetTests(SutekhTest):
    """class for the Card Set tests"""
    aAbstractCards = ['.44 magnum', 'ak-47', 'abbot', 'abebe', 'abombwe']
    aCardExpansions = [('.44 magnum', 'Jyhad'),
            ('ak-47', 'LotN'),
            ('abbot', 'Third Edition'),
            ('abombwe', 'Legacy of Blood')]
    aCardSetNames = ['Test Set 1', 'Test Set 2']

    def _fill_phys_cards(self):
        """Fill contents of the physical card table"""
        aAddedPhysCards = []
        for sName in self.aAbstractCards:
            oAC = IAbstractCard(sName)
            oPC = PhysicalCard(abstractCard=oAC, expansion=None)
            aAddedPhysCards.append(oPC)
        for sName, sExpansion in self.aCardExpansions:
            oAC = IAbstractCard(sName)
            oExpansion = IExpansion(sExpansion)
            oPC = PhysicalCard(abstractCard=oAC, expansion=oExpansion)
            aAddedPhysCards.append(oPC)
        return aAddedPhysCards

    def test_physical_card_set(self):
        """Test physical card set handling"""
        # pylint: disable-msg=E1101, R0915, R0914
        # E1101: SQLObject + PyProtocols magic confuses pylint
        # R0915, R0914: Want a long, sequentila test case to minimise
        # repeated setups, so it has lots of lines + variables
        aAddedPhysCards = self._fill_phys_cards()
        # We have a physical card list, so create some physical card sets
        oPhysCardSet1 = PhysicalCardSet(name=self.aCardSetNames[0])
        oPhysCardSet1.comment = 'A test comment'
        oPhysCardSet1.author = 'A test author'

        self.assertEqual(oPhysCardSet1.name, self.aCardSetNames[0])
        self.assertEqual(oPhysCardSet1.comment, 'A test comment')
        oPhysCardSet2 = PhysicalCardSet(name=self.aCardSetNames[1],
                comment='Test 2', author=oPhysCardSet1.author)
        self.assertEqual(oPhysCardSet2.name, self.aCardSetNames[1])
        self.assertEqual(oPhysCardSet2.author, oPhysCardSet1.author)
        self.assertEqual(oPhysCardSet2.comment, 'Test 2')

        oPhysCardSet3 = IPhysicalCardSet(self.aCardSetNames[0])

        self.assertEqual(oPhysCardSet1, oPhysCardSet3)

        oPhysCardSet4 = PhysicalCardSet.byName(self.aCardSetNames[1])
        self.assertEqual(oPhysCardSet2, oPhysCardSet4)

        # Add cards to the physical card sets

        for iLoop in range(5):
            oPhysCardSet1.addPhysicalCard(aAddedPhysCards[iLoop].id)
            oPhysCardSet1.syncUpdate()

        self.assertEqual(len(oPhysCardSet1.cards), 5)
        self.assertEqual(MapPhysicalCardToPhysicalCardSet.selectBy(
            physicalCardID = aAddedPhysCards[0]).count(), 1)
        self.assertEqual(MapPhysicalCardToPhysicalCardSet.selectBy(
            physicalCardID = aAddedPhysCards[7]).count(), 0)

        for iLoop in range(3, 8):
            oPhysCardSet2.addPhysicalCard(aAddedPhysCards[iLoop].id)
            oPhysCardSet2.syncUpdate()

        self.assertEqual(len(oPhysCardSet2.cards), 5)
        self.assertEqual(MapPhysicalCardToPhysicalCardSet.selectBy(
            physicalCardID = aAddedPhysCards[0]).count(), 1)
        self.assertEqual(MapPhysicalCardToPhysicalCardSet.selectBy(
            physicalCardID = aAddedPhysCards[4]).count(), 2)

        # Check output

        oWriter = PhysicalCardSetWriter()
        self.assertEqual(oWriter.gen_xml_string(oPhysCardSet1.name),
            oWriter.gen_xml_string(oPhysCardSet3.name))
        sExpected = '<physicalcardset author="A test author" ' \
                'comment="A test comment" name="Test Set 1" '\
                'sutekh_xml_version="1.1"><annotations /><card count="1" ' \
                'expansion="None Specified" id="11" name="Abebe" /><card ' \
                'count="1" expansion="None Specified" id="1" ' \
                'name=".44 Magnum" /><card count="1" expansion="None ' \
                'Specified" id="8" name="Abbot" /><card count="1" ' \
                'expansion="None Specified" id="2" name="AK-47" /><card ' \
                'count="1" expansion="None Specified" id="14" ' \
                'name="Abombwe" /></physicalcardset>'
        self.assertEqual(oWriter.gen_xml_string(oPhysCardSet1.name),
                sExpected)

        sTempFileName =  self._create_tmp_file()
        fOut = open(sTempFileName, 'w')
        oWriter.write(fOut, self.aCardSetNames[0])
        fOut.close()
        oIdFile = IdentifyXMLFile()
        tResult = oIdFile.id_file(sTempFileName)
        self.assertEqual(tResult[0], 'PhysicalCardSet')
        tResult = oIdFile.parse_string(sExpected)
        self.assertEqual(tResult[0], 'PhysicalCardSet')

        sPCS2 = oWriter.gen_xml_string(self.aCardSetNames[1])

        # Check Deletion

        for oCard in oPhysCardSet1.cards:
            oPhysCardSet1.removePhysicalCard(oCard.id)

        self.assertEqual(len(oPhysCardSet1.cards), 0)
        PhysicalCardSet.delete(oPhysCardSet1.id)

        self.assertRaises(SQLObjectNotFound, PhysicalCardSet.byName,
            self.aCardSetNames[0])

        delete_physical_card_set(self.aCardSetNames[1])

        self.assertRaises(SQLObjectNotFound, PhysicalCardSet.byName,
            self.aCardSetNames[1])

        self.assertEqual(MapPhysicalCardToPhysicalCardSet.selectBy(
            physicalCardID = aAddedPhysCards[0]).count(), 0)
        self.assertEqual(MapPhysicalCardToPhysicalCardSet.selectBy(
            physicalCardID = aAddedPhysCards[4]).count(), 0)

        # Check input

        oParser = PhysicalCardSetParser()
        fIn = open(sTempFileName, 'r')
        oParser.parse(fIn)
        fIn.close()
        oParser.parse_string(sPCS2)

        oPhysCardSet1 = IPhysicalCardSet(self.aCardSetNames[0])

        self.assertEqual(len(oPhysCardSet1.cards), 5)
        self.assertEqual(MapPhysicalCardToPhysicalCardSet.selectBy(
            physicalCardID = aAddedPhysCards[0]).count(), 1)
        self.assertEqual(MapPhysicalCardToPhysicalCardSet.selectBy(
            physicalCardID = aAddedPhysCards[7]).count(), 1)
        self.assertEqual(len(oPhysCardSet2.cards), 5)
        self.assertEqual(MapPhysicalCardToPhysicalCardSet.selectBy(
            physicalCardID = aAddedPhysCards[4]).count(), 2)


    def test_abstract_card_set(self):
        """Test abstract card set handling"""
        # pylint: disable-msg=E1101, R0915, R0914
        # E1101: SQLObject + PyProtocols magic confuses pylint
        # R0915, R0914: Want a long, sequentila test case to minimise
        # repeated setups, so it has lots of lines + variables
        oAbsCardSet1 = AbstractCardSet(name=self.aCardSetNames[0])
        oAbsCardSet1.comment = 'A test comment'
        oAbsCardSet1.author = 'A test author'

        self.assertEqual(oAbsCardSet1.name, self.aCardSetNames[0])
        self.assertEqual(oAbsCardSet1.comment, 'A test comment')
        oAbsCardSet2 = AbstractCardSet(name=self.aCardSetNames[1],
                comment='Test 2', author=oAbsCardSet1.author)
        self.assertEqual(oAbsCardSet2.name, self.aCardSetNames[1])
        self.assertEqual(oAbsCardSet2.author, oAbsCardSet1.author)
        self.assertEqual(oAbsCardSet2.comment, 'Test 2')

        oAbsCardSet3 = IAbstractCardSet(self.aCardSetNames[0])

        self.assertEqual(oAbsCardSet1, oAbsCardSet3)

        oAbsCardSet4 = AbstractCardSet.byName(self.aCardSetNames[1])
        self.assertEqual(oAbsCardSet2, oAbsCardSet4)

        # Test addition

        for sName in self.aAbstractCards:
            oAC = IAbstractCard(sName)
            oAbsCardSet1.addAbstractCard(oAC)
            oAbsCardSet2.addAbstractCard(oAC)
            if sName != self.aAbstractCards[2]:
                oAbsCardSet2.addAbstractCard(oAC)

        self.assertEqual(len(oAbsCardSet1.cards), 5)
        self.assertEqual(len(oAbsCardSet2.cards), 9)
        self.assertEqual(MapAbstractCardToAbstractCardSet.selectBy(
            abstractCardID=IAbstractCard(self.aAbstractCards[0]).id).count(),
            3)
        self.assertEqual(MapAbstractCardToAbstractCardSet.selectBy(
            abstractCardID=IAbstractCard(self.aAbstractCards[2]).id).count(),
            2)

        # check output
        oWriter = AbstractCardSetWriter()
        sExpected = '<abstractcardset author="A test author" ' \
                'comment="A test comment" name="Test Set 1" ' \
                'sutekh_xml_version="1.1"><annotations /><card count="1" ' \
                'id="11" name="Abebe" /><card count="1" id="8" name="Abbot" ' \
                '/><card count="1" id="1" name=".44 Magnum" /><card ' \
                'count="1" id="2" name="AK-47" /><card count="1" id="14" ' \
                'name="Abombwe" /></abstractcardset>'
        self.assertEqual(oWriter.gen_xml_string(self.aCardSetNames[0]),
                sExpected)
        sTempFileName =  self._create_tmp_file()
        fOut = open(sTempFileName, 'w')
        oWriter.write(fOut, self.aCardSetNames[1])
        fOut.close()
        oIdFile = IdentifyXMLFile()
        tResult = oIdFile.id_file(sTempFileName)
        self.assertEqual(tResult[0], 'AbstractCardSet')
        tResult = oIdFile.parse_string(sExpected)
        self.assertEqual(tResult[0], 'AbstractCardSet')

        # check Deletion

        for oCard in oAbsCardSet1.cards:
            oAbsCardSet1.removeAbstractCard(oCard.id)

        self.assertEqual(len(oAbsCardSet1.cards), 0)
        AbstractCardSet.delete(oAbsCardSet1.id)

        self.assertRaises(SQLObjectNotFound, AbstractCardSet.byName,
            self.aCardSetNames[0])

        delete_abstract_card_set(self.aCardSetNames[1])

        self.assertRaises(SQLObjectNotFound, AbstractCardSet.byName,
            self.aCardSetNames[1])

        self.assertEqual(MapAbstractCardToAbstractCardSet.selectBy(
            abstractCardID=IAbstractCard(self.aAbstractCards[0]).id).count(),
            0)
        self.assertEqual(MapAbstractCardToAbstractCardSet.selectBy(
            abstractCardID=IAbstractCard(self.aAbstractCards[2]).id).count(),
            0)

        # check input
        oParser = AbstractCardSetParser()

        oParser.parse_string(sExpected)
        fIn = open(sTempFileName, 'r')
        oParser.parse(fIn)
        fIn.close()

        oAbsCardSet1 = IAbstractCardSet(self.aCardSetNames[0])
        oAbsCardSet2 = IAbstractCardSet(self.aCardSetNames[1])

        self.assertEqual(len(oAbsCardSet1.cards), 5)
        self.assertEqual(len(oAbsCardSet2.cards), 9)
        self.assertEqual(MapAbstractCardToAbstractCardSet.selectBy(
            abstractCardID=IAbstractCard(self.aAbstractCards[0]).id).count(),
            3)
        self.assertEqual(MapAbstractCardToAbstractCardSet.selectBy(
            abstractCardID=IAbstractCard(self.aAbstractCards[2]).id).count(),
            2)

if __name__ == "__main__":
    unittest.main()