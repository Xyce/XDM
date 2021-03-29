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

from xdm import Types
from xdm.exceptions import InvalidTypeException
from xdm.exceptions import NameConflictException
from xdm.index import *
from xdm.index.UID import UID
from xdm.statements.commands import Command
from xdm.statements.nodes import LAZY_STATEMENT
from xdm.statements.nodes.ENODE import ENODE
from xdm.statements.nodes.devices import Device
from xdm.statements.nodes.models import MASTER_MODEL
from xdm.statements.nodes.models.modeldefs import ModelDef
from xdm.statements.refs.Ref import Ref


class NAME_SCOPE_INDEX(MasterIndex):
    """ An index for tracking names including their respective
        scope.  This index extends MasterIndex and can therefore
        register other indices.  When using add() or more specific
        variants (add_model(), add_enode(), etc...), this class
        will propogate adds to the respective indices.
        """

    def __init__(self, parent=None, subckt_command=None, lib_command=None):
        MasterIndex.__init__(self)
        self._children = []
        self._parent = parent
        self._statements = {}
        self._all_statements_in_scope = {}
        # only used in child scopes to define subckt name
        self._subckt_command = subckt_command
        self._lib_command = lib_command
        self._child_scope_lib_sects = []
        self._name_to_statement = {}

        if parent is not None:
            self._lsi = parent.lazy_statement_index
            self._uid = parent.uid_index
            self._sli = parent.source_line_index
            self._commands_index = parent.commands_index
            self._indexes = parent.indexes
        else:
            self._lsi = LAZY_STATEMENT_INDEX()
            self._uid = UID()
            self._sli = SRC_LINE_INDEX()
            self._commands_index = COMMANDS_INDEX()
            self.add_index(self._lsi)
            self.add_index(self._uid)
            self.add_index(self._sli)
            self.add_index(self._commands_index)

    def __hash__(self):
        if self._subckt_command:
            return hash(self._subckt_command.uid)
        if self._lib_command:
            return hash(self._lib_command.uid)
        return hash(None)

    def __eq__(self, other):
        if other is None:
            return self is None
        elif other.subckt_command:
            return self._subckt_command == other.subckt_command
        elif other.lib_command:
            return self._lib_command == other.lib_command

    @property
    def indexes(self):
        return self._indexes

    @property
    def statements(self):
        return self._statements

    @property
    def all_statements_in_scope(self):
        return self._all_statements_in_scope

    def push_scope(self, subckt_command=None, lib_command=None):
        """
        .. _push-scope:

        returns NAME_SCOPE_INDEX

        Creates a new child scope.  Child scopes can see the entire
        scope of their ancestors, but not their descendants.

        Returns:
            NAME_SCOPE_INDEX. A new child scope to the current scope
        """
        if subckt_command:
            self._children.append(NAME_SCOPE_INDEX(self, subckt_command=subckt_command))
        elif lib_command:
            self._children.append(NAME_SCOPE_INDEX(self, lib_command=lib_command))

        return self._children[-1]

    def pop_scope(self):
        """ returns parent scope (or self if no parent)

        Returns the parent scope.  Used when a child scope
        has ended (like the end of a sub circuit.

        Returns:
           NAME_SCOPE_INDEX. Parent scoped object
        """
        if self._parent is not None:
            return self._parent

        return self

    def add(self, st, case_insensitive=False):
        """
        Generic add function.  This takes in ModelDef, Device, ENODE, and str.
        If the object is a str, then it will assume this is a lazy object (type
        is not yet known).

        Args:
           st (ModelDef, Device, ENODE, or str): Object to add to index
           case_insensitive

        Throws:
           InvalidTypeException. Raised if st is of an unknown type
        """
        if isinstance(st, ModelDef):
            self.add_model(st, case_insensitive=case_insensitive)
        elif isinstance(st, Device):
            self.add_device(st, case_insensitive=case_insensitive)
        elif isinstance(st, ENODE):
            self.add_enode(st, case_insensitive=case_insensitive)
        elif isinstance(st, Ref):
            self.add_ref(st)
        elif isinstance(st, LAZY_STATEMENT):
            self.add_lazy_statement(st)
        elif isinstance(st, Command):
            st.set_prop(Types.statementType, "__COMMAND__")
            self._add_statement(st)
        #        elif isinstance(st, SUBCKT):
        #            st.set_prop(Types.statementType, "__SUBCKT__")
        #            self._add_statement(st, case_insensitive=case_insensitive)
        else:
            raise InvalidTypeException(st + ' must be of type ModelDef, Device, ENODE, or str')

    def add_model(self, m, case_insensitive=False):
        """
        Adds a model to the scope.  It takes in a ModelDef and either adds it
        to an existing MASTER_MODEL, or creates a new MASTER_MODEL and adds it
        to the scope.  All ModelDefs and MASTER_MODEL must be defined within
        the same scope.

        The ModefDef is also passed to existing indexes to be properly indexed.
        The MASTER_MODEL is passed to existing indexes when it is created.

        Args:
           m (ModelDef): Model added to scope
           case_insensitive

        Returns:
           MASTER_MODEL: parent of ModelDef

        Throws:
           NameConflictException if there is another object with the same name as
           m that is not a corresponding MASTER_MODEL or MASTER_MODEL within
           the same scope.

           InvalidModelException if m is not a ModelDef

        """
        master = None

        # type checking
        if not isinstance(m, ModelDef):
            raise InvalidTypeException(m.name + " is not of type ModeDef")

        # If MASTER_MODEL already exists
        model_name = m.name
        if case_insensitive:
            model_name = m.name.upper()

        if ("__MODELDEF__" + model_name) in self._statements and isinstance(
                self._statements[("__MODELDEF__" + model_name)], MASTER_MODEL):
            master = self._statements[("__MODELDEF__" + model_name)]
        else:
            d = self.get_object("__LAZYSTATEMENT__" + model_name)
            master = MASTER_MODEL(m.name)
            if isinstance(d, LAZY_STATEMENT):
                d.bind(master, case_insensitive)
                self.remove_statement(d)
            if self._lib_command is None:
                if self.scope_contains("__MODELDEF__" + model_name):
                    raise NameConflictException(model_name + " has already been used in this scope")
            else:
                if self.local_scope_contains("__MODELDEF__" + model_name):
                    raise NameConflictException(model_name + " has already been used in this scope")

            self._statements["__MODELDEF__" + model_name] = master
            # Put MASTER_MODEL in indexes (if any care to see it)
            self._add_to_indexes(master)

        m.set_prop(Types.statementType, "__MODELDEF__")
        master.add_model(m)

        # Add ModelDef to indexes
        self._add_to_indexes(m)

        return master

    def add_enode(self, e, case_insensitive=False):
        """

        Adds a ENODE to the scope tree.

        ENODES will not bind to LAZY_STATEMENTs and attempts to add an ENODE that
        conflicts with a LAZY_STATEMENT will get a NameConflictException

        Args:
           e (Statement): Statement to add to scoping
           case_insensitive

        Throws:
           NameConflictException if the name conflicts with another name within the scope
        """
        if isinstance(e, ENODE):
            e.set_prop(Types.statementType, "__ENODE__")
            self._add_statement(e, case_insensitive)
        else:
            raise InvalidTypeException(e.name + " is not of type ENODE")

    def add_ref(self, st):
        """

        Adds a Ref to the scope tree.

        Args:
           st (Statement): Statement to add to scoping
        """
        if isinstance(st, Ref):
            st.set_prop(Types.statementType, "__REF__")
            self._add_statement(st)
        else:
            raise InvalidTypeException(st.name + " is not of type Ref")

    def remove_statement(self, st):
        if st.name in self._statements:
            del (self._statements[st.name])
        else:
            if self._parent is not None:
                self._parent.remove_statement(st)

    def _add_statement(self, st, is_device=False, case_insensitive=False):
        # If it is a named statement, we need to check if there
        # is a name/scope conflict. Directives, for example,
        # do not need to be checked.
        name = st.name
        if case_insensitive:
            name = name.upper()

        if name is not None:
            self._all_statements_in_scope[st.get_prop(Types.statementType) + name] = st
            # check if lazy statement
            d = self.get_object("__LAZYSTATEMENT__" + name)

            if d:
                d.bind(st, case_insensitive)
                self.remove_statement(d)

            if isinstance(st, Device):
                if self.contains(st.get_prop(Types.statementType) + st.device_type + name):
                    raise NameConflictException(
                        str(st.device_type + name) + " has already been used in this scope")
                self._statements[st.get_prop(Types.statementType) + st.device_type + name] = st

            elif isinstance(st, ENODE) or (isinstance(st, Command) and st.command_type == ".SUBCKT"):
                if self.get_object(st.get_prop(Types.statementType) + name):
                    # only raise exception and exit if the name scope conflict occurs at the top scope
                    # otherwise, just give warning since child scopes won't affect what's actually to
                    # be simulated
                    if self.is_top_parent():
                        raise NameConflictException(str(name) + " has already been used in this scope")
                    else:
                        logging.warning(str(name) + " duplicated in a child scope. Continuing.")
                self._statements[st.get_prop(Types.statementType) + name] = st

            elif isinstance(st, Ref):
                self._statements[st.get_prop(Types.statementType) + str(st.uid)] = st
            else:
                self._statements[st.get_prop(Types.statementType) + name] = st
        else:
            self._all_statements_in_scope[st.get_prop(Types.statementType) + str(st.uid)] = st

        self._add_to_indexes(st)

    def _add_to_indexes(self, st):
        for idx in self._get_indexes(st):
            idx.add(st)

    @property
    def named_statements(self):
        return self._statements.values()

    def add_device(self, st, case_insensitive=False):
        """

        Adds a statement to the scope tree.

        If LAZY_STATEMENT was added:

        Takes in a statement and finds its LAZY_OBJECT equivilent, and
        updates the scope tree (remove LAZY_OBJECT and add to current scope).
        It also calls bind() on the LAZY_OBJECT so all referencing Statements
        can be updated to reference to the correct object.

        Args:
           st (Statement): Statement to add to scoping
           case_insensitive

        Throws:
           NameConflictException if the name conflicts with another name within the scope
        """
        if isinstance(st, Device):
            st.set_prop(Types.statementType, "__DEVICE__")
            self._add_statement(st, True, case_insensitive)
            self._name_to_statement[st.get_prop(Types.name)] = st
        else:
            raise InvalidTypeException(st.name + " is not of type Device")

    def add_lazy_statement(self, nm, uid):
        st = LAZY_STATEMENT(nm, uid, self)

        st.set_prop(Types.statementType, "__LAZYSTATEMENT__")
        self._add_statement(st)

        return st

    def _child_contains(self, nm):
        for c in self._children:
            if c.contains(nm) or c.child_contains(nm):
                return True

        return False

    def _parent_contains(self, nm):
        if self._parent is None:
            return False

        if self._parent.contains(nm):
            return True

        return self._parent._parent_contains(nm)

    def contains(self, nm):
        """
        Checks to see if a name is within a scope node

        Args:
           nm (str): Name of scoped variable

        Returns:
           bool. True if the name is within scoped node; else false
        """
        return nm in self._statements

    def get_object(self, nm):
        """
        Returns object (if exists) with the name nm thats within the scope
        space.  If the name is within the scope space, then it exists within
        the current scope or a predecessor's scope (not a child).

        Args:
           nm (str): Name of scoped variable

        Returns:
           Statement.  None if there is no nm within the scope
        """
        if self.contains(nm):
            return self._statements[nm]
        if self._parent is None:
            return None

        return self._parent.get_object(nm)

    def scope_contains(self, nm):
        """
        Checks to see if a name is within the current scope

        Args:
           nm (str): Name of scoped variable

        Returns:
           bool. True if the name is within scope; else false
        """
        return self.contains(nm) or self._parent_contains(nm)

    def local_scope_contains(self, nm):
        """
        Checks to see if a name is within just the local scope

        Args:
           nm (str): Name of scoped variable

        Returns:
           bool. True if the name is within scope; else false
        """
        return self.contains(nm)

    @property
    def parent(self):
        """ returns the parent

        Returns:
            NAME_SCOPE_INDEX. The parent object.
        """
        return self._parent

    @property
    def children(self):
        """ returns list of children

        Returns:
            list. All the direct children of a scope.
        """
        return self._children

    @property
    def lazy_statement_index(self):
        return self._lsi

    def get_statement_by_name(self, name_string):
        return self._name_to_statement.get(name_string)

    @property
    def uid_index(self):
        return self._uid

    @property
    def source_line_index(self):
        return self._sli

    @property
    def commands_index(self):
        return self._commands_index

    @lazy_statement_index.setter
    def lazy_statement_index(self, lsi):
        self._lsi = lsi

    @uid_index.setter
    def uid_index(self, uid):
        self._uid = uid

    @source_line_index.setter
    def source_line_index(self, sli):
        self._sli = sli

    def is_top_parent(self):
        return not self._parent

    # TODO figure out if this is deprecated??? doesn't seem to be, self._subckt_name isn't set anywhere!
    @property
    def scope_name(self):
        return self._subckt_name

    # TODO figure out if this is deprecated???
    @property
    def full_scope_name(self):
        full_scope_name = ""
        scope = self
        stack = []
        while scope.subckt_name is not None:
            stack.append(scope.subckt_name)
            scope = scope.parent

        return ":".join(reversed(stack))

    @property
    def subckt_command(self):
        return self._subckt_command

    @property
    def lib_command(self):
        return self._lib_command

    def warn_case_sensitivity(self):
        """
        Checks and warns for naming conflicts that could arise.  This is a potential problem translating from a
        case-sensitive language (e.g., Spectre) to a case-insensitive language (e.g., Xyce).  xdm's behavior is to
        warn and do nothing to the output.  It would result in a re-definition error in Xyce (e.g., multiple
        devices named the same and defined twice).
        """
        # dictionary from lower-cased name list of actual cased names
        upper_to_actual = {}
        warning_message_keys = []
        for statement in self._statements.keys():
            statement_upper = statement.upper()
            if statement_upper in upper_to_actual:
                warning_message_keys.append(statement_upper)
                upper_to_actual[statement_upper].append(statement)
            else:
                upper_to_actual[statement_upper] = [statement]

        for warning_message_key in set(warning_message_keys):
            conflicting_names_list = upper_to_actual[warning_message_key]
            groomed_list = []

            for item in conflicting_names_list:
                parts = item.split("__")
                groomed_list.append(parts[2])

            groomed_list.sort()

            warning_string = "xdm Detected multiple "
            if "__DEVICE__" in warning_message_key:
                warning_string += "devices"
            elif "__ENODE__" in warning_message_key:
                warning_string += "nodes"
            elif "__MODELDEF__" in warning_message_key:
                warning_string += "models"
            elif "__SUBCKT__" in warning_message_key:
                warning_string += "subcircuit definitions"
            else:
                # warning_string += "statements"
                # TURNS OFF WARNING FOR ANYTHING BUT DEVICE, ENODE, MODELDEF, OR SUBCKT
                continue
            warning_string += " with the same case-insensitive names: " + str(groomed_list)

            logging.warning(warning_string)

        for child in self._children:
            child.warn_case_sensitivity()

    def get_child_scope(self, child_name):
        for child in self._children:
            if not child.subckt_command is None:
                if child.subckt_command.name == child_name:
                    return child
            if not child.lib_command is None:
                if child.lib_command.props["LIB_ENTRY"] == child_name:
                    return child
            # if child.subckt_command.name == child_name or child.lib_command.name == child_name:
            #     return child
        return None

    def add_child_scope_lib_sects(self, lib_sect):
        self._child_scope_lib_sects.append(lib_sect)

    @property
    def child_scope_lib_sects(self):
        return self._child_scope_lib_sects

    def retroactive_add_statement(self, child):
        self.all_statements_in_scope.update(child.all_statements_in_scope)

        for child_lib_sect in child.child_scope_lib_sects:
            new_child = self.get_child_scope(child_lib_sect)
            self.retroactive_add_statement(new_child)

