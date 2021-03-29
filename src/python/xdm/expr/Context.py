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

from xdm import Types
import SpiritExprCommon
from xdm.expr.expr_utils import find_expr_components


class Context(object):
    """A class to store all the relevant parameters and functions for a device
       instantiation.
    """
    def __init__(self, hier, scopes):
        # list of device name and subckt name pairs, i.e. [("X1", "abc"), ("X2", "def"), ...]
        self._full_hier = hier
        self._scopes_in_context = scopes
        self._scope_names = []
        self._st_in_context = []
        # device hierarcy, i.e. X1:X2: ...
        self._device_hierarchy = ""

        self._funcs_to_evaluate = []
        self._func_hierarchy = []
        self._func_expr = []
        self._func_dict = {}
        self._func_arg_dict = {}
        self._param_list = []
        self._disallowed_funcs = ["EXP", "LOG", "SQRT", "MAX", "MIN", "AGAUSS", "LIMIT", "SIN", "COS",
                                  "TAN", "ATAN", "PI", "INT", "ABS", "LOG10"]

        for subckt_scope in self._scopes_in_context:
            self._st_in_context.append(subckt_scope.all_statements_in_scope)
            self._scope_names.append(subckt_scope.subckt_command.name)

        for device_name, subckt_name in self._full_hier:
            self._device_hierarchy += device_name + ":"

    def __str__(self):
        return "Device hierarchy = " + str(self._full_hier) + "\nScopes = " + str(self._scopes_in_context) + "\nScope Names = " + str(self._scope_names)

    def context_exists(self, curr_hier, scopes_to_include):
        return curr_hier == self._full_hier and scopes_to_include == self._scopes_in_context

    def nonterminal_context(self, curr_hier):
        temp_hier = []
        for hier in self._full_hier:
            temp_hier.append(hier)
            if curr_hier == temp_hier:
                return True
        return False

    def find_funcs_to_be_evaluated(self, global_context=False):
        self.find_in_devices_and_subckts()
        self.find_in_param_statements(global_context)
        self.find_func_definitions()
        return

    def find_in_devices_and_subckts(self):
        if self._full_hier:
            # store parameters from subckt definitions and device instantiations in a dict temporarily.
            # this is for easy overwriting of parameters
            param_dict = {}

            for devname, subckt in self._full_hier:
                # first, find default instance parameters for subcircuit
                for ind, scope_dict in enumerate(self._st_in_context):
                    for key in scope_dict:
                        i = scope_dict[key]
                        if i.props[Types.statementType] == "__COMMAND__" and "MY_NAME" in i.props:
                            if i.props["MY_NAME"] == subckt and "SUBCIRCUIT_PARAMS_LIST" in i.props:
                                for param in i.props["SUBCIRCUIT_PARAMS_LIST"]:
                                    param_dict[param] = i.props["SUBCIRCUIT_PARAMS_LIST"][param].upper().strip("{").strip("}")

                # next, find device instantiation parameters
                devname = devname[1:]
                for ind, scope_dict in enumerate(self._st_in_context):
                    for key in scope_dict:
                        i = scope_dict[key]
                        if i.props[Types.statementType] == "__DEVICE__" and "SUBCIRCUIT_PARAMS_LIST" in i.props:
                            if i.props["MY_NAME"] == devname:
                                for param in i.props["SUBCIRCUIT_PARAMS_LIST"]:
                                    param_dict[param] = i.props["SUBCIRCUIT_PARAMS_LIST"][param].upper().strip("{").strip("}")

            for param in param_dict:
                self._param_list.append(param.upper() + "=" + param_dict[param])

        return

    def find_in_param_statements(self, global_context):
        func_tokens = [SpiritExprCommon.expr_data_model_type.FUNC_NAME, SpiritExprCommon.expr_data_model_type.BUILTIN_FUNC, SpiritExprCommon.expr_data_model_type.FUNC_BEGIN, SpiritExprCommon.expr_data_model_type.FUNC_END, SpiritExprCommon.expr_data_model_type.FUNC_ARG]

        # find rest of param statements
        for ind, scope_dict in enumerate(self._st_in_context):
            # determine what scope it's currently in
            subckt = self._scope_names[ind]

            curr_hier = ""
            if subckt:
                for device_name, subckt_name in self._full_hier:
                    curr_hier += device_name + ":"
                    if subckt == subckt_name:
                        break

            scope_sorted_by_line = []
            for key in scope_dict:
                i = scope_dict[key]
                if i.line_num is None:
                    scope_sorted_by_line.append((i, 0))
                else:
                    scope_sorted_by_line.append((i, i.line_num[0]))

            scope_sorted_by_line = sorted(scope_sorted_by_line, key=lambda x: x[1])

            for elem in scope_sorted_by_line:
                i = elem[0]

                if i.props[Types.statementType] == "__COMMAND__":
                    if i.command_type == ".PARAM":
                        for param in i.props["PARAMS_LIST"]:
                            curr_funcs = []

                            value = i.props["PARAMS_LIST"][param].upper()
                            if value.startswith("{"):
                                # for the case XDM hack put curly braces around simple function calls
                                # xyce translation, remove them for the purposes of HSPICE function
                                # name parsing
                                value = value[1:-1]
                                find_expr_components(i.props["PARAMS_LIST"][param][1:-1], func_tokens, curr_funcs)
                            else:
                                find_expr_components(i.props["PARAMS_LIST"][param], func_tokens, curr_funcs)
                            self._param_list.append(param.upper() + "=" + value)

                            if curr_funcs:
                                func_call = ""
                                curr_func_name = ""
                                for curr_func in curr_funcs:
                                    if curr_func.types[0] == SpiritExprCommon.expr_data_model_type.FUNC_END:
                                        func_call = func_call[:-1] + curr_func.value
                                        if not curr_func_name.upper() in self._disallowed_funcs:
                                            if global_context or (not global_context and ":" in curr_hier):
                                                # self._funcs_to_evaluate.append(curr_hier + param + "," + func_call.replace(" ", "").upper())
                                                self._func_hierarchy.append(curr_hier + param)
                                                self._func_expr.append(func_call.replace(" ", "").upper())

                                        func_call = ""
                                        curr_func_name = ""
                                    elif curr_func.types[0] == SpiritExprCommon.expr_data_model_type.FUNC_ARG:
                                        func_call += curr_func.value + ","
                                    elif (curr_func.types[0] == SpiritExprCommon.expr_data_model_type.FUNC_NAME or
                                          curr_func.types[0] == SpiritExprCommon.expr_data_model_type.BUILTIN_FUNC):
                                        curr_func_name = curr_func.value
                                        func_call += curr_func.value
                                    else:
                                        func_call += curr_func.value
        return

    def find_func_definitions(self):
        # finally, find all functions
        for scope_dict in self._st_in_context:
            for key in scope_dict:
                i = scope_dict[key]
                if i.props[Types.statementType] == "__COMMAND__":
                    if i.command_type == ".FUNC":
                        self._func_dict[i.props["FUNC_NAME_VALUE"].upper()] = i.props["FUNC_EXPRESSION"].upper()
                        self._func_arg_dict[i.props["FUNC_NAME_VALUE"].upper()] = [x.upper() for x in i.props["FUNC_ARG_LIST"]]
        return

    def add_st_to_context(self, statements, name):
        self._st_in_context.append(statements)
        self._scope_names.append(name)
        return

    @property
    def full_hier(self):
        return self._full_hier

    @property
    def scopes_in_context(self):
        return self._scopes_in_context

    @property
    def scope_names(self):
        return self._scope_names

    @property
    def st_in_context(self):
        return self._st_in_context

    @property
    def device_hierarchy(self):
        return self._device_hierarchy

    @property
    def funcs_to_evaluate(self):
        return self._funcs_to_evaluate

    @property
    def func_hierarchy(self):
        return self._func_hierarchy

    @property
    def func_expr(self):
        return self._func_expr

    @property
    def func_dict(self):
        return self._func_dict

    @property
    def func_arg_dict(self):
        return self._func_arg_dict

    @property
    def param_list(self):
        return self._param_list
