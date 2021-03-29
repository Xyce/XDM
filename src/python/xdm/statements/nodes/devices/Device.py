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


import logging
from collections import OrderedDict

import xdm.Types as Types
from xdm.exceptions import InvalidModelException
from xdm.exceptions import InvalidTypeException
from xdm.statements import Statement
from xdm.statements.nodes import LAZY_STATEMENT
from xdm.statements.nodes.models import MASTER_MODEL


class Device(Statement):
    """
    Represents the parent class for all devices

    Throws:
        InvalidTypeException. Raised if props is not string or dict
    """

    def __init__(self, props, params, fl, line_num, uid, m_param=None):
        Statement.__init__(self, fl, line_num, uid, props, params)

        self._device_level = None
        self._device_level_key = None
        self._device_version = None
        self._device_version_key = None
        self._device_type = None
        self._device_local_type = None
        self._m_param = m_param
        self._resolve_control_devices = False

    def __str__(self):
        return 'Type=' + str(self.__class__) + ' Name=' + str(self.name) + ' Model=' + str(self.model)

    def bind(self, o, case_insensitive=False):
        """
        Binds object to its respective LAZY_STATEMENT

        Args:
            o (Model): Model to bind to
            case_insensitive
        """
        if self.is_valid_bind(o, case_insensitive):
            if isinstance(o, MASTER_MODEL) and self.model is None:
                self.model = o
            return

        # raise InvalidBindException(o.name + "(" +
        #                            str(o.__class__) +
        #                            ") can not be bound to " + self.name)

    @property
    def model(self):
        """
        Returns a device's model or None if the device has no model

        Returns:
           MASTER_MODEL. if a model has been set (otherwise None)
        """
        return self.get_prop(Types.modelName)

    @model.setter
    def model(self, model):
        """
        Sets the model for a Device.  If a model was previously set, this
            is overridden.

        Args:
            model (MASTER_MODEL or LAZY_STATEMENT): The device's model

        Throws:
            InvalidModelException if model is not a valid Model
        """
        if isinstance(model, MASTER_MODEL):
            self.props[Types.modelName] = model
        else:
            raise InvalidModelException(model.name + "(" +
                                        str(model.__class__) +
                                        ") is not a MASTER_MODEL")

    def set_amb_data(self, key, types):
        """
        Device received ambigous data, but can't be referenced

        Args:
           key (str): Key
           types (array of types (str)): Possible types
        """
        self._amb_types[key] = types

    def resolve_lazy_bind(self, string, name_scope_index, is_case_insensitive=False):
        """
        Called at the end of parsing all input to resolve lazy statements
            associated with this device

        Args:
           string (str): String key of lazy statement
           name_scope_index (NAME_SCOPE_INDEX): Scope of this lazy statement
           is_case_insensitive
        """
        # need to uppercase string
        if isinstance(name_scope_index.get_object("__LAZYSTATEMENT__" + string), LAZY_STATEMENT):
            string_upper_if_insensitive = string
            if is_case_insensitive:
                string_upper_if_insensitive = string_upper_if_insensitive.upper()
            model = name_scope_index.get_object("__MODELDEF__" + string_upper_if_insensitive)
            if model:
                for device in name_scope_index.get_object("__LAZYSTATEMENT__" + string).listener:
                    device.model = model
                name_scope_index.remove_statement(name_scope_index.get_object("__LAZYSTATEMENT__" + string))
            else:
                # it is not a model
                if MASTER_MODEL in self.lazy_statements[string]:
                    self.lazy_statements[string].remove(MASTER_MODEL)
                if len(self.lazy_statements[string]) == 1:
                    self.add_param(self.lazy_statements[string][0], string)

    def add_prop(self, prop_key, prop_value):
        """
        Adds property to props dictionary

        Args:
           prop_key (str, Types): Key
           prop_value (str, structure): Value (currently stores all values as string or structure)
        """
        self.props[prop_key] = prop_value

    @property
    def device_type(self):
        """
        Gets the Xyce type of this device

        Returns:
           device_type (str)
        """
        return self._device_type

    @property
    def device_local_type(self):
        """
        Gets the local (i.e., Spectre) type of this device

        Returns:
           device_local_type (str)
        """
        return self._device_local_type

    @property
    def device_level(self):
        """
        Gets the level of this device

        Returns:
           device_level (str): level is local to the language
        """
        return self._device_level

    @property
    def device_level_key(self):
        """
        Gets the level key of this device

        Returns:
           device_level_key (str): level key is mapping to Xyce Data Model representation of level
        """
        return self._device_level_key

    @property
    def device_version(self):
        """
        Gets the version of this device

        Returns:
           device_version (str): version is local to the language
        """
        return self._version

    @property
    def device_version_key(self):
        """
        Gets the version key of this device

        Returns:
           device_version_key (str): version key is mapping to Xyce Data Model representation of version
        """
        return self._device_version_key

    @device_type.setter
    def device_type(self, device_type):
        """
        Sets the type of this device

        :Example:
            .. code-block:: python

                device.device_type = "D"
        """
        self._device_type = device_type

    @device_local_type.setter
    def device_local_type(self, device_local_type):
        """
        Sets the local type of this device (i.e., vcvs in Spectre, E in SPICE)

        :Example:
            .. code-block:: python

                device.device_local_type = "D"
        """
        self._device_local_type = device_local_type

    @device_level.setter
    def device_level(self, device_level):
        """
        Sets the level of this device

        :Example:
            .. code-block:: python

                device.device_level = "2"
        """
        self._device_level = device_level

    @device_level_key.setter
    def device_level_key(self, device_level_key):
        """
        Sets the level key (Xyce Data Model representation) of this device

        :Example:
            .. code-block:: python

                device.device_level_key = "D1"
        """
        self._device_level_key = device_level_key

    @device_version.setter
    def device_version(self, device_version):
        """
        Sets the version of this device

        :Example:
            .. code-block:: python

                device.device_version = "2"
        """
        self._device_version = device_version

    @device_version_key.setter
    def device_version_key(self, device_version_key):
        """
        Sets the version key (Xyce Data Model representation) of this device

        :Example:
            .. code-block:: python

                device.device_version_key = "D1"
        """
        self._device_version_key = device_version_key

    @property
    def resolve_control_devices(self):
        """
        Gets the flag for further processing of control devices
        """
        return self._resolve_control_devices

    @resolve_control_devices.setter
    def resolve_control_devices(self, boolean):
        """
        Sets the flag for further processing of control devices
        """
        self._resolve_control_devices = boolean

    def resolve_control_device_list(self, index, reader_state):
        """
        Resolves control devices to Device objects for this device.  Logs warning if
            device is not found in this scope.

        Args:
           index (NAME_SCOPE_INDEX): Scope of this device
           reader_state
        """
        if self.props.get(Types.controlDeviceList):
            new_device_list = []
            for control_device_string in self.props[Types.controlDeviceList]:
                device_string_with_case = control_device_string
                if reader_state.is_store_device_prefix():
                    device_string_with_case = "L" + device_string_with_case
                if reader_state.is_case_insensitive():
                    device_string_with_case = device_string_with_case.upper()
                device = index.get_object("__DEVICE__" + device_string_with_case)
                if device:
                    new_device_list.append(device)
                else:
                    logging.warning("Control Device for " + self.props[
                        Types.name] + " not found.  Control Device: " + device_string_with_case)
            self.props[Types.controlDeviceList] = new_device_list
        if self.props.get(Types.controlDeviceValue):
            device_string_with_case = self.props[Types.controlDeviceValue]
            if reader_state.is_case_insensitive():
                device_string_with_case = device_string_with_case.upper()
            device = index.get_object("__DEVICE__" + device_string_with_case)
            if device:
                self.props[Types.controlDeviceValue] = device
            else:
                logging.warning("Control Device for " + self.props[
                    Types.name] + " not found.  Control Device: " + device_string_with_case)
        if self.props.get(Types.polyExpression):
            new_device_list = []
            for control_device_string in self.props[Types.polyExpression].poly_control_list:
                device_string_with_case = control_device_string
                if reader_state.is_case_insensitive():
                    device_string_with_case = device_string_with_case.upper()
                device = index.get_object("__DEVICE__" + device_string_with_case)
                if device:
                    new_device_list.append(device)
                else:
                    logging.warning("Control Device for " + self.props[
                        Types.name] + " not found.  Control Device: " + device_string_with_case)
            self.props[Types.polyExpression].poly_control_list = new_device_list
