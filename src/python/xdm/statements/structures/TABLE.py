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


from xdm.inout.writers.writer_utils import replace_inner_curly_braces


class TABLE(object):
    """
    A structure to represent a table.  It is used in:
    - Current Controlled Voltage Source
    - Voltage Controlled Voltage Source
    - Voltage Controlled Current Source
    - Nonlinear Dependent Source

    Lookup tables provide a means of specifying a piecewise
    linear function in an expression.  A table expression is
    specified with the keyword TABLE followed by an expression
    that is evaluated as the independent variable of the
    function, followed by a list of pairs of independent
    variable/dependent variable values.

    It has the following structure:
        TABLE{<expression>} = <(<input value>,<output value>)>*

    For example:
        B1 1 0 V={TABLE {time} = (0, 0) (1, 2) (2, 4) (3, 6)}
    """

    def __init__(self, table_expression, table_pairs):
        # TODO: link this to an actual expression object
        self._table_expression = table_expression
        self._table_pairs = table_pairs

    @property
    def table_expression(self):
        return self._table_expression

    @property
    def table_pairs(self):
        return self._table_pairs

    def spice_string(self, delimiter=' '):
        formatted_pairs = ''

        for table_pair in self._table_pairs:
            formatted_pair = ''
            formatted_pair += '('
            formatted_pair += table_pair[0]
            formatted_pair += ','
            formatted_pair += table_pair[1]
            formatted_pair += ')'
            formatted_pair += delimiter
            formatted_pairs += formatted_pair

        formatted_pairs = formatted_pairs

        return_string = ''
        return_string += 'TABLE'
        return_string += delimiter
        return_string += replace_inner_curly_braces(self._table_expression)
        return_string += '='
        return_string += formatted_pairs.strip()

        return return_string
