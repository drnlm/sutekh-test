# CardSetManagementMenu.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Menu for the CardSet View's
# Copyright 2006 Neil Muller <drnlmuller+sutekh@gmail.com>
# Copyright 2006 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Menu for the card set list"""

import gtk
from sutekh.gui.FilteredViewMenu import FilteredViewMenu

class CardSetManagementMenu(FilteredViewMenu):
    """Card Set List Management menu.
       """
    # pylint: disable-msg=R0904
    # gtk.Widget, so many public methods
    def __init__(self, oFrame, oWindow, oController):
        super(CardSetManagementMenu, self).__init__(oFrame, oWindow,
                oController)
        self.__sName = 'Card Set List'
        self.__sSetTypeName = 'Card Set'
        self._oController = oController
        self.__create_actions_menu()
        self.create_edit_menu()
        self.create_filter_menu()
        self.add_plugins_to_menus(self._oFrame)

    # pylint: disable-msg=W0201
    # called from __init__, so OK
    def __create_actions_menu(self):
        """Add the Actions Menu"""
        oMenu  = self.create_submenu(self, "_Actions")
        self.create_menu_item('Create New Card Set', oMenu,
                self._oController.create_new_card_set)
        self.create_menu_item('Edit Card Set Properties', oMenu,
                self._oController.edit_card_set_properties)
        self.create_menu_item('Mark/UnMark Card Set as in use', oMenu,
                    self._oController.toggle_in_use_flag)
        self.create_menu_item('Delete selected Card Set', oMenu,
                self._oController.delete_card_set, 'Delete')
        oMenu.add(gtk.SeparatorMenuItem())
        self.add_common_actions(oMenu)

    # pylint: enable-msg=W0201
