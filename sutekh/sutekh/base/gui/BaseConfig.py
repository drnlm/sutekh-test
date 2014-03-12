# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Config handling object
# Wrapper around configobj and validate with some hooks for Sutekh purposes
# Copyright 2007 Neil Muller <drnlmuller+sutekh@gmail.com>
# Copyright 2010 Simon Cross <hodgestar+sutekh@gmail.com>
# License: GPL - See COPYRIGHT file for details

"""Base classes and constants for configuation management."""

from validate import is_list

# Type definitions
CARDSET = 'Card Set'
FRAME = 'Frame'
FULL_CARDLIST = 'cardlist'
CARDSET_LIST = 'cardset list'

# Reserved filter names (for filter in profile special cases)
DEF_PROFILE_FILTER = 'No profile filter'

def is_option_list(sValue, *aOptions):
    """Validator function for option_list configspec type."""
    return [is_option(sMem, *aOptions) for sMem in is_list(sValue)]

