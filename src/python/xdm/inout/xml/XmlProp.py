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


class XmlProp(object):
    """
    Represents an xdm Prop, which is a property defined in XML that typically
    does not have default values.  They also do not usually have key-value pair
    syntax (this=that).  Examples of props are e-nodes, model names, and
    device-specific expressions.

    Member variables:
        prop_type (e.g., node, modelName, tableExpression)

        label (language-specific key for the value stored)

        label_key (symbol key value that is stored)

        value (default value, which is rare for a prop)

        output_alias (used in Spectre as the node alias name in output variables)

        nested (used for nested props, only PSpice options)

        nested_propType (used for nested props, only PSpice options)
    """
    def __init__(self, prop_type, label, label_key, value, output_alias=None):
        self._prop_type = prop_type
        self._label = label
        self._label_key = label_key
        self._value = value
        self._nested = None
        self._nested_propType = None
        self._output_alias = output_alias

    def print_me(self):
        print("    ----------- ")
        if self._nested:
            print("        XmlProp Nested Type:", self._nested_propType)
        print("        XmlProp Type:", self._prop_type)
        print("        XmlProp Label:", self._label)
        print("        XmlProp Label Key:", self._label_key)
        print("        XmlProp Value:", self._value)
        print("        XmlProp Output Alias:", self._output_alias)

    @property
    def prop_type(self):
        return self._prop_type

    @property
    def label(self):
        return self._label

    @property
    def label_key(self):
        return self._label_key

    @property
    def value(self):
        return self._value

    @property
    def nested(self):
        return self._nested

    @nested.setter
    def nested(self, nested_val):
        self._nested = nested_val

    @property
    def output_alias(self):
        return self._output_alias

    @property
    def nested_propType(self):
        return self._nested_propType

    @nested_propType.setter
    def nested_propType(self, propType_val):
        self._nested_propType = propType_val
