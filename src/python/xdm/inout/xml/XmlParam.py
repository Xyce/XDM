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


class XmlParam(object):
    """
    Represents an xdm Param, which is a property defined in XML that typically
    has default values and usually have key-value pair
    syntax (this=that).  Examples of params are resistance, capacitance, and inductance.

    Member variables:
        param_type (e.g., R, C, L)

        label (language-specific key for the value stored)

        label_key (symbol key value that is stored)

        value (default value)

        nested (used for nested props, only PSpice options)

        nested_propType (used for nested props, only PSpice options)

        m_flag (not sure if this is needed - might be handled already in XmlDeviceType)
    """
    def __init__(self, param_type, label, label_key, value, m_flag=None):
        self._param_type = param_type
        self._label = label
        self._label_key = label_key
        self._value = value
        self._nested = None
        self._nested_paramType = None
        self._m_flag = m_flag

    def print_me(self):
        print("    ----------- ")
        if self._nested:
            print("        XmlParam Nested Type:", self._nested_paramType)
        print("        XmlParam Type:", self._param_type)
        print("        XmlParam Label:", self._label)
        print("        XmlParam Label Key:", self._label_key)
        print("        XmlParam Value:", self._value)
        print("        XmlParam MFlag:", self._m_flag)

    @property
    def param_type(self):
        return self._param_type

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
    def m_flag(self):
        return self._m_flag

    @property
    def nested(self):
        return self._nested

    @property
    def nested_paramType(self):
        return self._nested_paramType

    @nested.setter
    def nested(self, nested_val):
        self._nested = nested_val

    @nested_paramType.setter
    def nested_paramType(self, paramType_val):
        self._nested_paramType = paramType_val
