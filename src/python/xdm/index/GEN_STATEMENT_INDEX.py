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


from bisect import bisect_left

from xdm.index.StatementIndex import StatementIndex
from xdm.exceptions import InvalidTypeException
from xdm.statements import Statement


class GEN_STATEMENT_INDEX(StatementIndex):
    """
    A general indexing class for indexing objects by a specified attribute.
    Each entry in the index can be stored in a sorted order.

    Args:
       f (function): Returns the indexable attribute

       s (function): Returns the sortable attribute

       t (Class): Type checking for index.  Anything added, must be of type t.
    """
    def __init__(self, f, s=None, t=Statement):
        """
        Initializes a GEN_STATEMENT_INDEX.  This takes in two functions.  The
        first takes in the indexable object and returns the indexable
        attribute.  The second takes in the same object and returns the field
        to sort over.

        Args:
           f (function): Returns the indexable attribute

           s (function): Returns the sortable attribute
        """
        self._file_dict = {}
        self._file_dict_keys = {}
        self._f = f
        self._s = s
        self._t = t

        self._iter_keys = []
        self._iter_counter = 0

    @property
    def type(self):
        return self._t

    def add(self, ws):
        """
        Adds a Statement to the index

        Args:
           ws (Statement): Statement to be indexed

        """
        if not isinstance(ws, self._t):
            raise InvalidTypeException(ws.__class__.__name__ + " is not instance of " + self._t.__name__)

        # get the files name
        nm = self._f(ws)

        # if first entry, then create array
        if nm not in self._file_dict:
            self._file_dict[nm] = []
            self._file_dict_keys[nm] = []

        if self._s is not None:
            # get the line number
            key = self._s(ws)

            # find the position in the list that the statement 
            # belongs in, then insert both the key and the statement
            # at that position
            key_pos = bisect_left(self._file_dict_keys[nm], key)
            self._file_dict_keys[nm].insert(key_pos, key)
            self._file_dict[nm].insert(key_pos, ws)
        else:
            self._file_dict[nm].append(ws)

    def get_statements(self, fl):
        """
        Gets all statements that have the indexable attribute equal to fl

        Args:
           fl (Object): Object representing an indexable attribute

        Returns:
           list. List of objects with the indexable attribute equal to fl
        """
        if fl in self._file_dict:
            return self._file_dict[fl]

        return None

    @property
    def statement_dict(self):
        return self._file_dict

    def __len__(self):
        return len(self._file_dict.keys())

    def __iter__(self):
        self._iter_keys = list(self._file_dict.keys())
        self._iter_counter = 0
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self._iter_counter >= len(self._iter_keys):
            raise StopIteration
        else:
            self._iter_counter += 1
            return (self._iter_keys[self._iter_counter - 1],
                    self._file_dict[self._iter_keys[self._iter_counter - 1]])
