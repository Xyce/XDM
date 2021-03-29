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


from xdm.statements.nodes.devices import *


class POLY(object):
    """
    POLY provides a compact method of specifying polynomial expressions in which
    the variables in the polynomial are specified followed by an ordered list of
    polynomial coefficients. All expressions specified with POLY are ultimately
    translated by Xyce into an equivalent, straightforward polynomial expression
    in a B source.

    There are three different syntax forms for POLY, which can be a source of confusion.
    - the E and G sources (voltage-dependent voltage or current sources) use one form
    - the F and H sources (current-dependent voltage or current sources) use a second form
    - the B source (general nonlinear source) a third form

    All three formats of POLY express the same three components:
    - a number of variables involved in the expression (N, the number in parentheses
    after the POLY keyword)
    - the variables themselves
    - an ordered list of coefficients for the polynomial terms

    Voltage-controlled POLY format requires specification of two nodes for each voltage
    on which the source depends.  There must therefore be twice as many nodes as the
    number of variables specified in parentheses after the POLY keyword.  Example:

        Epoly 1 2 POLY(3) n1p n1m n2p n2m n3p n3m

    Current-controlled POLY format requires specification of one voltage source name for
    each current on which the source depends. There must therefore be exactly as many nodes
    as the number of variables specified in parentheses after the POLY keyword.  Example:

        Fpoly 1 2 POLY(3) V1 V2 V3

    Finally, the most general form of POLY is that used in the general nonlinear dependent
    source, the B source. In this variant, each specific variable must be named explicitly
    (i.e. not simply by node name or by voltage source name), because currents and voltages
    may be mixed as needed. Examples:

        Bpoly 1 2 V={POLY(3) I(V1) V(2,3) V(3) ...}
        Bpoly2 1 2 I={POLY(3) I(V1) V(2,3) V(3) ...}
    """

    def __init__(self, poly_value, poly_control_list, poly_coeff_list):
        self._poly_value = poly_value
        # either list of node pairs, or list of control devices
        self._poly_control_list = poly_control_list
        self._poly_coeff_list = poly_coeff_list

    @property
    def poly_value(self):
        return self._poly_value

    @property
    def poly_control_list(self):
        return self._poly_control_list

    @property
    def poly_coeff_list(self):
        return self._poly_coeff_list

    @poly_value.setter
    def poly_value(self, x):
        self._poly_value = x

    @poly_control_list.setter
    def poly_control_list(self, x):
        self._poly_control_list = x

    @poly_coeff_list.setter
    def poly_coeff_list(self, x):
        self._poly_coeff_list = x

    def spice_string(self, delimiter=' '):
        formatted_control_list = ''
        formatted_coeff_list = ''

        for value in self._poly_control_list:
            if isinstance(value, tuple):
                formatted_control_list += value[0].name
                formatted_control_list += delimiter
                formatted_control_list += value[1].name
                formatted_control_list += delimiter
            elif isinstance(value, Device):
                formatted_control_list += value.device_type
                formatted_control_list += value.name
                formatted_control_list += delimiter

        for value in self._poly_coeff_list:
            formatted_coeff_list += value
            formatted_coeff_list += delimiter

        return_string = ''
        return_string += 'POLY'
        return_string += '('
        return_string += self._poly_value
        return_string += ')'
        return_string += delimiter
        return_string += formatted_control_list.strip()
        return_string += delimiter
        return_string += formatted_coeff_list.strip()

        return return_string
