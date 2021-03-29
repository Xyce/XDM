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


from xdm.exceptions import InvalidModelException
from xdm.statements import Statement
from xdm.statements.nodes.models.modeldefs import ModelDef


class MASTER_MODEL(Statement):
    """
    Holds one to many ModelDefs.  If multiple ModelDefs, then interpolation
    can be performed
    """
    def __init__(self, name):
        Statement.__init__(self, None, None, None, name)
        self._models = []

    def add_model(self, m):
        """
        Adds a model to a MASTER_MODEL.  Typically, a MASTER_MODEL only needs
        one ModelDef.  However, models that can be interpolated in Xyce will
        result in multiple ModelDefs.

        The ModelDef must have the same name as the MASTER_MODEL

        Args:
           m (ModelDef): A model definition

        Throws:
           InvalidModelException if m is not a ModelDef or has a different name
        """
        if not isinstance(m, ModelDef) or not m.name.upper() == self.name.upper():
            raise InvalidModelException(m.name +
                                        " is not a valid ModelDef")

        self._models.append(m)

    @property
    def models(self):
        """
        Returns all models held by the MASTER_MODEL

        Returns:
           list. A list of models
        """
        return self._models

    @property
    def device_type(self):
        if len(self._models) == 1:
            return self._models[0].device_type
        # TODO: Need to enforce device type/level in add_model?
        return None

    @property
    def device_level(self):
        if len(self._models) == 1:
            return self._models[0].device_level
        # TODO: Need to enforce device type/level in add_model?
        return None

    @property
    def device_level_key(self):
        if len(self._models) == 1:
            return self._models[0].device_level_key
        # TODO: Need to enforce device type/level in add_model?
        return None

    @property
    def device_version(self):
        if len(self._models) == 1:
            return self._models[0].device_version
        return None

    @property
    def device_version_key(self):
        if len(self._models) == 1:
            return self._models[0].device_version_key
        return None
