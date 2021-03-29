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


from xdm.inout.xml.XmlDeviceType import XmlDeviceType
from xdm.inout.xml.XmlDirectiveType import XmlDirectiveType
from collections import Counter
from xdm.exceptions import InvalidTypeException


class XmlLanguageDefinition(object):
    """
    Defines the language based on the xml file for a particular language-version pair.
    Composed of objects from this xml source directory.

    Member variables:
        language (e.g., pspice, spectre)

        version (version of the language)

        device_types (dictionary of device name to XmlDeviceType)

        directive_types (dictionary of directive name to XmlDirectiveType)

        unsupported_directive_list (list of unsupported directives in xdm from this language)

        case_insensitive (whether this language is case insensitive)

        is_store_device_prefix (whether the device prefix should be appended in a control device list)

        admin_dict (special variables to determine whether to employ a hack or perform some other function)
    """
    def __init__(self, language, version, case_insensitive=False, store_device_prefix=False):
        self._language = language
        self._version = version
        self._device_types = {}
        self._directive_types = {}
        self._unsupported_directive_list = []
        self._case_insensitive = case_insensitive
        self._is_store_device_prefix = store_device_prefix
        self._admin_dict = {}

    def __hash__(self):
        return hash((self._language, self._version))

    def __eq__(self, other):
        return (self._language, self._version) == (other.language, other.version)

    def add_device_type(self, device_type):
        if isinstance(device_type, XmlDeviceType):
            if not self._device_types.get(device_type.name):
                self._device_types[device_type.name] = []
            self._device_types[device_type.name].append(device_type)
        else:
            raise InvalidTypeException(device_type + " is not of type DeviceType")

    @property
    def device_types(self):
        # flatten each grouped list of devices b/c values are each individual lists
        return [item for sublist in self._device_types.values() for item in sublist]

    def add_directive_type(self, directive_type):
        if isinstance(directive_type, XmlDirectiveType):
            self._directive_types[directive_type.identity()] = directive_type
        else:
            raise InvalidTypeException(directive_type + " is not of type DirectiveType")

    @property
    def directive_types(self):
        return self._directive_types.values()

    @property
    def unsupported_directive_list(self):
        return self._unsupported_directive_list

    @unsupported_directive_list.setter
    def unsupported_directive_list(self, unsupported_directive_list):
        self._unsupported_directive_list = unsupported_directive_list

    def print_me(self):
        print("Language:", self._language, "Version:", self._version)

    @property
    def language(self):
        return self._language

    @property
    def version(self):
        return self._version

    def get_devices_by_name(self, name):
        return self._device_types.get(name)

    def get_devices_by_local_name(self, local_name):
        matched_device_name_list = []
        for device_type in [item for sublist in self._device_types.values() for item in sublist]:
            if device_type.is_device_local_name(local_name):
                matched_device_name_list.append(device_type)
        return matched_device_name_list

    # TODO: we need to consolidate
    def get_device_by_name_level(self, name, level, version=""):
        return self.get_device(name, level, version)

    def get_device_by_name_level_key(self, level_key, version_key=""):
        for device_type in [item for sublist in self._device_types.values() for item in sublist]:
            if device_type.is_device_level_key(level_key):
                if version_key:
                    if device_type.is_device_version_key(version_key):
                        return device_type
                else:
                    return device_type
        return None

    def get_device(self, name, level, version=""):
        if self._device_types.get(name):
            for device_type in self._device_types[name]:
                if device_type.is_device_level(level):
                    if version:
                        if device_type.is_device_version(version):
                            return device_type
                    else:
                        return device_type
        return None

    def get_default_definition(self, local_name):
        candidate_devices = self.get_devices_by_local_name(local_name)
        if len(candidate_devices) == 1:
            return candidate_devices[0]
        elif len(candidate_devices) > 1:
            for device_type in candidate_devices:
                if device_type.is_device_name(local_name) and device_type.is_default():
                    return device_type
        return None

    def get_directive_by_name(self, name):
        return self._directive_types.get(name)

    def get_control_type(self, language_device_types):
        control_type_bag = Counter()
        for device in language_device_types:
            control_type_bag[device.get_prop_value("controlType")] += 1
        if len(control_type_bag) == 1:
            return list(control_type_bag.elements())[0]

    def is_case_insensitive(self):
        return self._case_insensitive

    @property
    def admin_dict(self):
        return self._admin_dict

    @admin_dict.setter
    def admin_dict(self, admin_dict):
        self._admin_dict = admin_dict

    def is_store_device_prefix(self):
        return self._is_store_device_prefix
