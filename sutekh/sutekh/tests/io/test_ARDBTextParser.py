# test_ARDBTextParser.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2007 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Test case for ARDB text parser"""

from sutekh.io.ARDBTextParser import ARDBTextParser
import unittest

class DummyHolder(object):
    """Emulate CardSetHolder for test purposes."""
    def __init__(self):
        self.aCards = []
        # pylint: disable-msg=C0103
        # placeholder names for CardSetHolder attributes
        self.name = ''
        self.comment = ''
        self.author = ''

    def add(self, iCnt, sName, sExpName):
        """Add a card to the dummy holder."""
        self.aCards.append((iCnt, sName))

class ARDBTextParserTests(unittest.TestCase):
    """class for the ARDB/FELDB text input parser"""
    sTestText1 = """
        Deck Name : Test Deck
        Author : Anon Y Mous
        Description :
        Simple test deck.

        http://www.example.url/in/description

        Crypt [3 vampires] Capacity min: 2 max: 10 average: 7.33
       ------------------------------------------------------------
        2x Test Vamp 1			  10 ...
        1x Test Vamp 2			  2  ...
        ...

        Library [19 cards]
        ------------------------------------------------------------
        Action [6]
            2x Test Card 1
            4x Test Card 2

        Action Modifier [12]
            12x Test Card 3

        Reaction [1]
            1x Test Card 4
        ...
    """

    sTestText2 = """
        Deck Name : Test Deck 2
        Author : Anon Y Mous
        Description : Simple test deck.
        Crypt: (3 vampires, Min: 2, Max: 10 Ave: 7.33)
       ------------------------------------------------------------
        2 Test Vamp 1			  aus dom for   10 ...
        1 Test Vamp 2			  DOM for obf   2  ...
        ...

        Library [19 cards]
        ------------------------------------------------------------
        Action [6]
        2 Test Card 1
        4 Test Card 2

        Action Modifier [12]
        12 Test Card 3

        Reaction [1]
        1 Test Card 4
        ...
    """


    def test_basic(self):
        """Run the input test."""
        oHolder = DummyHolder()
        oParser = ARDBTextParser(oHolder)

        for sLine in self.sTestText1.split("\n"):
            oParser.feed(sLine + "\n")

        self.assertEqual(oHolder.name, "Test Deck")
        self.assertEqual(oHolder.author, "Anon Y Mous")
        self.failUnless(oHolder.comment.startswith(
            "        Simple test deck."))
        self.failUnless(oHolder.comment.endswith("in/description\n\n"))

        aCards = oHolder.aCards

        self.assertEqual(len(aCards), 6)
        self.failUnless((2, "Test Vamp 1") in aCards)
        self.failUnless((1, "Test Vamp 2") in aCards)
        self.failUnless((2, "Test Card 1") in aCards)
        self.failUnless((4, "Test Card 2") in aCards)
        self.failUnless((12, "Test Card 3") in aCards)
        self.failUnless((1, "Test Card 4") in aCards)

        oHolder = DummyHolder()
        oParser = ARDBTextParser(oHolder)
        for sLine in self.sTestText2.split("\n"):
            oParser.feed(sLine + "\n")

        self.assertEqual(oHolder.name, "Test Deck 2")
        self.assertEqual(oHolder.author, "Anon Y Mous")
        self.failUnless(oHolder.comment.startswith(
            "Simple test deck."))

        aCards = oHolder.aCards

        self.assertEqual(len(aCards), 6)
        self.failUnless((2, "Test Vamp 1") in aCards)
        self.failUnless((1, "Test Vamp 2") in aCards)
        self.failUnless((2, "Test Card 1") in aCards)
        self.failUnless((4, "Test Card 2") in aCards)
        self.failUnless((12, "Test Card 3") in aCards)
        self.failUnless((1, "Test Card 4") in aCards)


if __name__ == "__main__":
    unittest.main()
