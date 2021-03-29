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


from collections import Counter, OrderedDict


class XmlDeviceType(object):
    """
    Defines a device-level pair and its associated parameters, model, and writers.

    Member variables:
        name (abstract data model name for this device)

        local_name (language-specific key for the value stored)

        level (language-specific level definition)

        levelKey (abstract data model reference to this device's device-level pair)

        version (language-specific version definition)

        versionKey (abstract data model reference to this device version)

        default (bool whether device level is default level, usually level 1)

        props (dictionary of language-specific key to prop)

        key_props (dictionary of abstract data model key to prop)

        params (dictionary of language-specific key to param)

        key_params (dictionary of abstract data model key to param)

        m_flag (may be obsolete now,  but used to define whether value gets multiplied or divided due to parallel/series
        definition of device m param)

        model (model definition for this device-level key)

        writer (XmlWriter for this device)

        ambiguity_token_list (list of tokens that define possible props/params for ambiguous statements)
    """
    def __init__(self, name, level, levelKey, version, versionKey, default=False, local_name=""):
        self.name = name
        self.local_name = local_name
        self.level = level
        self.levelKey = levelKey
        self.version = version
        self.versionKey = versionKey
        self.default = default
        self._props = OrderedDict()
        self._key_props = OrderedDict()
        self._params = OrderedDict()
        self._key_params = OrderedDict()
        self._m_flag = None
        self._model = None
        self._writer = None
        self._ambiguity_token_list = None

    def __hash__(self):
        return hash((self.name, self.level, self.levelKey, self.version))

    def __eq__(self, other):
        return (self.name, self.level, self.levelKey, self.version) == (other.name, other.level, other.levelKey, other.version)

    def add_prop(self, prop):
        self._props[prop.label] = prop
        if prop.label_key:
            self._key_props[prop.label_key] = prop

    def add_param(self, param):
        self._params[param.label] = param
        self._key_params[param.label_key] = param

        if param.m_flag:
            self._m_flag = param

    @property
    def props(self):
        return self._props

    @property
    def params(self):
        return self._params

    @property
    def key_params(self):
        return self._key_params

    def get_param(self, param):
        return self._params.get(param)

    def get_prop(self, prop):
        return self._props.get(prop)

    def get_prop_value(self, label, prop_type=None):
        value_counter = Counter()
        for prop in self._props:
            if label == prop.prop_type:
                value_counter[prop.label] += 1
        if len(value_counter) == 1:
            return list(value_counter.elements())[0]

    def print_me(self):
        print("Device name:", self.name, "Level:", self.level, "Level Key:",
              self.levelKey, "Version:", self.version)

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, model):
        self._model = model

    @property
    def writer(self):
        return self._writer

    @writer.setter
    def writer(self, writer):
        self._writer = writer

    @property
    def ambiguity_token_list(self):
        return self._ambiguity_token_list

    @ambiguity_token_list.setter
    def ambiguity_token_list(self, token_list):
        self._ambiguity_token_list = token_list

    @property
    def device_type(self):
        return self.name

    @property
    def device_local_type(self):
        return self.local_name

    @property
    def device_level(self):
        return self.level

    @property
    def device_level_key(self):
        return self.levelKey

    @property
    def device_version(self):
        return self.version

    @property
    def device_version_key(self):
        return self.versionKey

    @property
    def m_flag(self):
        return self._m_flag

    @m_flag.setter
    def m_flag(self, m_flag):
        self._m_flag = m_flag

    def identity(self):
        return self.levelKey

    def is_device_name(self, name):
        return self.name == name

    def is_device_local_name(self, local_name):
        return self.local_name == local_name

    def is_device_level(self, level):
        return self.level == level

    def is_device_level_key(self, level_key):
        return self.levelKey == level_key

    def is_device_version(self, version):
        return self.version == version

    def is_device_version_key(self, version_key):
        return self.versionKey == version_key

    def is_default(self):
        return self.default.lower() == "true"

    @property
    def control_type(self):
        return

    @property
    def node_types(self):
        node_types = []
        for key, value in self._props.items():
            if "node" == value.prop_type:
                node_types.append(value)
        return node_types
