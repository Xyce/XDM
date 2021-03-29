#-------------------------------------------------------------------------
#   Copyright 2002-2020 National Technology & Engineering Solutions of
#   Sandia, LLC (NTESS).  Under the terms of Contract DE-NA0003525 with
#   NTESS, the U.S. Government retains certain rights in this software.
#
#   This file is part of the Xyce(TM) XDM Netlist Translator.
#   
#   Xyce(TM) XDM is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#  
#   Xyce(TM) XDM is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#   
#   You should have received a copy of the GNU General Public License
#   along with the Xyce(TM) XDM Netlist Translator.
#   If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------


from xdm.statements import Statement


class LAZY_STATEMENT(Statement):
    """
    This class represents placeholders for statements that are referenced but not
    yet defined.
    """
    def __init__(self, name, uid, scope=None):
        Statement.__init__(self, None, None, uid, name)
        self._listeners = []
        self._scope = scope

    def add_listener(self, st):
        """
        Adds a Statement as a listener

        Args:
            st (Statement): A Statement that references this LAZY_STATEMENT
        """
        self._listeners.append(st)

    @property
    def listener(self):
        """
        Returns all Statements that reference this LAZY_NODE

        Returns:
            list.  List of Statement objects
        """
        return self._listeners

    def bind(self, st, case_insensitive=False):
        """
        Loops through all objects that reference the LAZY_STATEMENT and
        calls bind on each statement.

        Args:
            st (Node): Node object that is now defined
            case_insensitive
        """
        for d in self._listeners:
            d.bind(st, case_insensitive)

    @property
    def scope(self):
        """
        Returns the scope so that the proper scope is passed in when binding
        lazy statements after the end of parsing.

        Returns:
            scope: This item's scope
        """
        return self._scope

    @scope.setter
    def scope(self, scope):
        """
        Holds the scope so that the proper scope is passed in when binding
        lazy statements after the end of parsing.

        Args:
            scope (NAME_SCOPE_INDEX): Scope to be set
        """
        self._scope = scope
