# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Config handling object
# Wrapper around configobj and validate with some hooks for Sutekh purposes
# Copyright 2007 Neil Muller <drnlmuller+sutekh@gmail.com>
# Copyright 2010 Simon Cross <hodgestar+sutekh@gmail.com>
# License: GPL - See COPYRIGHT file for details

"""Configuration handling for the Sutekh GUI."""

from sutekh.gui.generic.BaseConfigFile import (BaseConfigFile, CARDSET,
        FRAME, PHYS_CARDLIST, CARDSET_LIST)
from sutekh.gui.AppConfig import PHYS_CARD_LIST_NAME
import pkg_resources


class ConfigFile(BaseConfigFile):
    """Add Sutekh specific bits to the config file handling
       """

    def _get_configspec(self):
        # pylint: disable-msg=E1101
        # pkg_resources confuses pylint here
        return pkg_resources.resource_stream(__name__, "configspec.ini")

    def sanitize(self):
        """Called after validation to clean up a valid config.

           Currently clean-up consists of adding some open panes if none
           are listed.
           """
        if not self._oConfig['open_frames']:
            # No panes information, so we set 'sensible' defaults
            self.add_frame(1, 'physical_card', PHYS_CARD_LIST_NAME, False,
                    False, -1, None)
            self.add_frame(2, 'Card Text', 'Card Text', False, False, -1, None)
            self.add_frame(3, 'Card Set List', 'Card Set List', False, False,
                    -1, None)
            self.add_frame(4, 'physical_card_set', 'My Collection', False,
                    False, -1, None)
