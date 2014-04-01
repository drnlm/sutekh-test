# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Config handling object
# Wrapper around configobj and validate with some hooks for Sutekh purposes
# Copyright 2007 Neil Muller <drnlmuller+sutekh@gmail.com>
# Copyright 2010 Simon Cross <hodgestar+sutekh@gmail.com>
# License: GPL - See COPYRIGHT file for details

"""Configuration handling for the Sutekh GUI."""

from sutekh.base.gui.BaseConfig import BaseConfigFile, is_option_list
import pkg_resources


class ConfigFile(BaseConfigFile):
    """Handle the setup and management of the config file.

       Ensure that the needed sections exist, and that sensible
       defaults values are assigned.

       Filters are saved to the config file, and interested objects
       can register as listeners on the config file to respond to
       changes to the filters.
       """
    # pylint: disable-msg=R0904, R0902
    # R0904 - We need to provide fine-grained access to all the data,
    # so lots of methods
    # R0902 - Lots of internal state, so lots of attributes

    dCustomConfigTypes = {
        'option_list': is_option_list,
    }

    def _get_app_configspec_file(self):
        """Get the correct config spec."""
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
            self.add_frame(1, 'physical_card', 'Full Card List', False,
                    False, -1, None)
            self.add_frame(2, 'Card Text', 'Card Text', False, False, -1, None)
            self.add_frame(3, 'Card Set List', 'Card Set List', False, False,
                    -1, None)
            self.add_frame(4, 'physical_card_set', 'My Collection', False,
                    False, -1, None)

    #
    # Application Level Config Settings
    #

    def get_icon_path(self):
        """Get the icon path from the config file"""
        return self._oConfig['main']['icon path']

    def set_icon_path(self, sPath):
        """Set the configured icon path"""
        self._oConfig['main']['icon path'] = sPath

