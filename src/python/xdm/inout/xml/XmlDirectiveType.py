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


from collections import OrderedDict


class XmlDirectiveType(object):
    """
    Defines a device-level pair and its associated parameters, model, and writers.

    Member variables:
        name (abstract data model name for this directive)

        props (dictionary of key to prop)

        params (dictionary of language-specific key to param)

        key_params (dictionary of abstract data model key to param)

        writer (XmlWriter for this directive)

        ambiguity_token_list (list of tokens that define possible props/params for ambiguous statements)

        nested (whether there are nested props below first level of props in this directive)

        nested_prop_dict (nested properties for .OPTIONS)
    """
    def __init__(self, name):
        self.name = name
        self._props = OrderedDict()
        self._params = OrderedDict()
        self._key_params = OrderedDict()
        self._writer = None
        self._ambiguity_token_list = None
        self._nested = None
        self._nested_prop_dict = {}

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def add_prop(self, prop):
        if len(prop.label_key) > 0:
            self._props[prop.label_key] = prop
        else:
            self._props[prop.label] = prop

    @property
    def props(self):
        return self._props

    def get_prop(self, prop):
        return self._props.get(prop)

    def add_param(self, param):
        self._params[param.label] = param
        self._key_params[param.label_key] = param

    @property
    def key_params(self):
        return self._key_params

    @property
    def params(self):
        return self._params

    def get_param(self, param):
        return self._params.get(param)

    def print_me(self):
        print(" ")
        print("== Directive name:", self.name)
        print("          Directive nested val:", self._nested)
        for prop in self._props:
            prop.print_me()

    @property
    def writer(self):
        return self._writer

    @writer.setter
    def writer(self, writer):
        self._writer = writer

    def add_nested_prop(self, key, prop):
        if not self._nested_prop_dict.get(key):
            self._nested_prop_dict[key] = []
        self._nested_prop_dict[key].append(prop)

    @property
    def nested_prop_dict(self):
        return self._nested_prop_dict

    @property
    def nested(self):
        return self._nested

    @nested.setter
    def nested(self, nested_val):
        self._nested = nested_val

    def is_directive_name(self, name):
        return self.name == name.upper()

    def identity(self):
        return self.name
