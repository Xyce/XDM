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


class XmlDeviceToken(object):
    """
    Token for the XmlWriter

    Member variables:
        order (order tokens should appear in output -- currently we just take order it appears in xml)

        ref (reference type, which directs the writer to the appropriate helper write function)

        value (explicit value, e.g., if printing out a string)

        required (whether this token must be written -- currently just doesn't get written if empty)

        label (reference key to abstract data model storage)

        include_list (which props/params should be written as a part of this token)

        exclude_list (which props/params should not be written as a part of this token)
    """
    def __init__(self, order, ref, value, required, label):
        self._order = order
        self._ref = ref
        self._value = value
        self._required = required
        self._label = label
        self._include_list = []
        self._exclude_list = []

        if self.ref == "pair":
            self._include_list = self.value[0]
            self._exclude_list = self.value[1]
            self._value = None

    def print_me(self):
        print("Order:", self.order, "Ref:", self.ref, "Value:", self.value,
              "Required:", self.required, "Label:", self.label)

    @property
    def order(self):
        return self._order

    @property
    def ref(self):
        return self._ref

    @property
    def value(self):
        return self._value

    @property
    def required(self):
        return self._required

    @property
    def label(self):
        return self._label

    @property
    def include_list(self):
        return self._include_list

    @property
    def exclude_list(self):
        return self._exclude_list
