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


class IC(object):
    """
        A structure to represent attributes of .IC, .DCVOLT and .NODESET statements. 
        Currently a WIP.

        This structure stores three attributes of the .IC statement:
            * The type of initial condition set (currently only voltage in Xyce)
            * The node the initial condition is set at
            * The value of the initial condition
    """

    def __init__(self, ic_type, ic_node, ic_value):
        self._ic_type = ic_type
        self._ic_node = ic_node
        self._ic_value = ic_value

    @property
    def ic_type(self):
        return self._ic_type

    @property
    def ic_node(self):
        return self._ic_node

    @property
    def ic_value(self):
        return self._ic_value
