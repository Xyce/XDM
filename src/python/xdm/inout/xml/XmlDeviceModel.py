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


class XmlDeviceModel(object):
    """
    Defines a model for a particular device-level pair, including its props, params, and writer.

    Member variables:
        props (like XmlDeviceType props, but for the model)

        params (like XmlDeviceType params, but for the model)

        key_params (like XmlDeviceType key_params, but for the model)

        device_type ("current" vs. "voltage", as needed)

        writer (list of XmlDeviceToken to write this model in this language)
    """
    def __init__(self):
        self._props = OrderedDict()
        self._params = OrderedDict()
        self._key_params = OrderedDict()
        self._device_type = None
        self._writer = None

    def add_prop(self, prop):
        if len(prop.label_key) > 0:
            self._props[prop.label_key] = prop
        else:
            self._props[prop.label] = prop

    def add_param(self, param):
        self._params[param.label] = param
        self._key_params[param.label_key] = param

    @property
    def props(self):
        return self._props

    @property
    def key_params(self):
        return self._key_params

    @property
    def params(self):
        return self._params

    def get_param(self, param):
        return self._params.get(param)

    def get_prop(self, prop):
        return self._props.get(prop)

    @property
    def writer(self):
        return self._writer

    @writer.setter
    def writer(self, writer):
        self._writer = writer

    @property
    def device_type(self):
        return self._device_type

    @device_type.setter
    def device_type(self, device_type):
        self._device_type = device_type

    def identity(self):
        return self._device_type.device_level_key

    def print_me(self):
        for prop in self._props:
            prop.print_me()
