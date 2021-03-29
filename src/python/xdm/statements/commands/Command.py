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
from collections import OrderedDict


class Command(Statement):
    """
    Parent class for all directives.
    """
    def __init__(self, props, params, fl, line_num, uid):
        """
        Initializes Directive

        Args:
           props (Dictionary): Key-value store for properties
           fl (str): Source file
           line_num (str): Line number form source file
           uid (int): Unique ID generated from UID
        """
        Statement.__init__(self, fl, line_num, uid, props, params)
        self._command_type = None
        self._command_local_type = None

    def __str__(self):
        return 'Type=' + str(self.__class__) + ' Name=' + str(self.name)

    @property
    def command_type(self):
        """
        Gets the type of this directive

        Returns:
           command_type (str)
        """
        return self._command_type

    @command_type.setter
    def command_type(self, command_type):
        """
        Sets the type of this directive

        :Example:
            .. code-block:: python

                directive.command_type = ".PRINT"
        """
        self._command_type = command_type

    @property
    def command_local_type(self):
        """
        Gets the local (i.e., Spectre) type of this directive

        Returns:
           command_local_type (str)
        """
        return self._command_local_type

    @command_local_type.setter
    def command_local_type(self, command_local_type):
        """
        Sets the local (i.e., Spectre) type of this directive

        :Example:
            .. code-block:: python

                directive.command_local_type = ".PRINT"
        """
        self._command_local_type = command_local_type
