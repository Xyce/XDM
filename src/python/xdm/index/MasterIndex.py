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


from xdm.index.StatementIndex import StatementIndex
from xdm.exceptions import InvalidTypeException


class MasterIndex(object):
    """ Holds a master list of all indexes applied to a data model.  this
    class should be extended as it does not actually apply the index.
    """

    def __init__(self):
        self._indexes = []

    def add_index(self, idx):
        """
        Adds an index  to the data model.

        Args:
           idx (StatementIndex): Statement index to add

        Throws:
           InvalidTypeException. If the user passes in idx that is of an incorrect type
        """
        if isinstance(idx, StatementIndex):
            self._indexes.append((idx.type, idx))
        else:
            raise InvalidTypeException(idx + " is not of type StatementIndex")

    def remove_index(self, idx):
        """
        Removes an index that was previously registered.

        Args:
           idx (StatementIdx): Index to be removed from the data model
        """
        for i, t in enumerate(self._indexes):
            if t[1] == idx:
                del(self._indexes[i])
                return

    def _get_indexes(self, st):
        """
        Protected method that gets all indexes who are tasked to index
        st.  For example, an index could be over just LAZY_STATEMENT.

        Args:
           st (Statement): Object that needs to be indexed

        Returns:
           list. List of all indexes who should index st
        """
        r = []

        for t in self._indexes:
            if isinstance(st, t[0]):
                r.append(t[1])

        return r
