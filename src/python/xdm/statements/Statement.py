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

from xdm import Types
from xdm.exceptions import InvalidTypeException
from xdm.exceptions import NotImplementedException


class Statement(object):
    """
    Represents a Statement within a netlist file.  The statement can
    be explicit, like a device.  Or the statement can be implicit, like
    a node belonging to a device.

    Member variables:
        fl (SOURCE_FILE object)
        line_num (int of line it was written from, None if implicit)
        uid (UID object - unique ID)
        lazy_statements (dictionary of (string value, possible types list))
        props (properties of the Statement - including)
    """

    def __init__(self, fl, line_num, uid, props, params=None):
        self._fl = fl
        self._line_num = line_num
        self._uid = uid
        self._lazy_statements = {}
        self._amb_types = {}
        self._inline_comment = None

        if isinstance(props, str):
            self._props = OrderedDict()
            self._props[Types.name] = props
        elif isinstance(props, dict):
            self._props = OrderedDict(props)
        elif props is None:
            self._props = OrderedDict()
        else:
            raise InvalidTypeException('props must be a dict or str')

        if isinstance(params, str):
            self._params = OrderedDict()
            self._params[Types.name] = params
        elif isinstance(params, dict):
            self._params = OrderedDict(params)
        elif params is None:
            self._params = OrderedDict()
        else:
            raise InvalidTypeException('params must be a dict or str')

    def __hash__(self):
        return hash(self._uid)

    def __eq__(self, other):
        if other is None:
            return self is None
        return self._uid == other.uid

    @property
    def lazy_statements(self):
        return self._lazy_statements

    @property
    def params(self):
        return self._params

    def get_param(self, p):
        return self._params.get(p)

    def add_param(self, param_key, param_value):
        """
        Adds property to params dictionary

        Args:
           param_key (str, Types): Key
           param_value (str, structure): Value (currently stores all values as string or structure)
        """
        self._params[param_key] = param_value

    @property
    def file(self):
        """
        Returns the file object where the statement belongs

        Returns:
           SourceFile. This statements source file
        """
        return self._fl

    @property
    def line_num(self):
        """
        Returns the line number this statement falls in its file (fl)

        Returns:
           int. line number within its contining file
        """
        return self._line_num

    @line_num.setter
    def line_num(self, line_num_int):
        self._line_num = []
        self._line_num.append(line_num_int)

    @property
    def uid(self):
        """
        Returns the unique ID object for this particular statement
        """
        return self._uid

    @property
    def inline_comment(self):
        return self._inline_comment

    @inline_comment.setter
    def inline_comment(self, comment):
        self._inline_comment = comment

    @property
    def name(self):
        return self.get_prop(Types.name)

    @property
    def props(self):
        return self._props

    def get_prop(self, p):
        return self._props.get(p)

    def bind(self, o):
        """
        This binds defined objects to LAZY_STATEMENT references.  This is
        an abstract function and should be defined by each statement that
        has bind capabilities

        Args:
            o (Node): Newly defined Node

        Throws:
            NotImplementedException for classes that do not have bind capabilities
        """
        raise NotImplementedException(type(o) + ' does not implement bind')

    def is_valid_bind(self, o, case_insensitive=False):
        """
        Called when attempting to bind an object, and returns True if the type of
        object is an instance of a class that exists in its list of potential
        class types.
        """
        name = o.name
        if case_insensitive:
            name = name.upper()
        for t in self._lazy_statements.get(name):
            if isinstance(t, str):
                return True
            elif isinstance(o, t):
                return True

        return False

    def finalize_bind(self):
        """
        Called after all lazy objects are bound, and returns True if no more lazy
        objects are attached to this statement.
        """
        if len(self._lazy_statements) > 0:
            return False
        return True

    def set_lazy_statement(self, o, types):
        """
        Sets a lazy object to a device.  This is used when o has not been properly
        defined when the current line is parsed.  The parser should know a list of
        possibilities and this is passed in as well.  When the object is defined,
        it will call bind causing this object to properly set references to o.

        Args:
           o (LAZY_STATEMENT): Object who has not yet been defined
           types (list<__class__>): List of all possible classes that o could be.

        Throws:
           InvalidTypeException. if o is not of type LAZY_STATEMENT
        """

        if 'add_listener' not in o.__class__.__dict__:
            raise InvalidTypeException(str(o) + " (" + str(o.__class__) + ") is not of type LAZY_STATEMENT")

        self._lazy_statements[o.name] = types
        o.add_listener(self)

    def set_prop(self, p, v):
        self._props[p] = v

    @property
    def untyped_props(self):
        """
        Convenience function to get all params.  All params do not exist inside
        the Types __dict__
        """
        new_dict = {}
        for key in self._props:
            match_bool = False
            for k in Types.__dict__:
                if Types.__dict__[k] == key:
                    match_bool = True
                    continue
            if not match_bool:
                new_dict[key] = self._props[key]

        return new_dict
