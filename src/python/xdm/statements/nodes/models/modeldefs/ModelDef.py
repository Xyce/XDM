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


from xdm.statements import Statement
from collections import OrderedDict


class ModelDef(Statement):
    """
    Parent class for all models defined by a netlist
    """

    def __init__(self, props, params, fl, line_num, uid):
        Statement.__init__(self, fl, line_num, uid, props, params)
        self._device_level = None
        self._device_type = None
        self._device_version = None
        self._device_local_type = None
        self._device_level_key = None
        self._device_version_key = None

    @property
    def device_type(self):
        """
        Gets the device type of this model

        Returns:
           device_type (str)
        """
        return self._device_type

    @property
    def device_local_type(self):
        """
        Gets the local device type of this model

        Returns:
           device_type (str)
        """
        return self._device_local_type

    @property
    def device_level(self):
        """
        Gets the device level of this model

        Returns:
           device_level (str): level is local to the language
        """
        return self._device_level

    @property
    def device_level_key(self):
        """
        Gets the device level key of this model

        Returns:
           device_level_key (str): level key is mapping to Xyce Data Model representation of level
        """
        return self._device_level_key

    @property
    def device_version(self):
        """
        Gets the device version of this model

        Returns:
           device_version (str): level is local to the language
        """
        return self._device_version

    @property
    def device_version_key(self):
        """
        Gets the device version key of this model

        Returns:
           device_version_key (str): version key is mapping to Xyce Data Model representation of version
        """
        return self._device_version_key

    @device_type.setter
    def device_type(self, device_type):
        """
        Sets the device type of this model

        :Example:
            .. code-block:: python

                model.device_type = "D"
        """
        self._device_type = device_type

    @device_local_type.setter
    def device_local_type(self, device_local_type):
        """
        Sets the local device type of this model

        :Example:
            .. code-block:: python

                model.device_type = "diode"
        """
        self._device_local_type = device_local_type

    @device_level.setter
    def device_level(self, device_level):
        """
        Sets the device level of this model

        :Example:
            .. code-block:: python

                model.device_level = "2"
        """
        self._device_level = device_level

    @device_level_key.setter
    def device_level_key(self, device_level_key):
        """
        Sets the device level key (Xyce Data Model representation) of this model

        :Example:
            .. code-block:: python

                model.device_level_key = "D1"
        """
        self._device_level_key = device_level_key

    @device_version.setter
    def device_version(self, device_version):
        """
        Sets the device version of this model

        :Example:
            .. code-block:: python

                model.device_version = "2"
        """
        self._device_version = device_version

    @device_version_key.setter
    def device_version_key(self, device_version_key):
        """
        Sets the device version key (Xyce Data Model representation) of this model

        :Example:
            .. code-block:: python

                model.device_version_key = "D1"
        """
        self._device_version_key = device_version_key
