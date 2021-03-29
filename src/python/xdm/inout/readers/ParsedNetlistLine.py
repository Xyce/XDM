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


class ParsedNetlistLine(object):
    """
    Intermediate data storage for a given netlist statement, which is then
    ingested into the appropriate object within the data model
    """

    def __init__(self, filename, linenum):
        self._type = ""  # mapped type
        self._local_type = ""
        self._name = ""
        self._filename = filename
        self._linenum = linenum
        self._params_dict = OrderedDict()
        self._known_objects = {}
        self._lazy_statements = OrderedDict()
        self._transient_values = []
        self._meas_dict = OrderedDict()
        self._output_variable_values = []
        self._func_arg_list = []
        self._value_list = []
        self._sweep_param_list = []
        self._schedule_param_list = []
        self._table_param_list = []
        self._poly_param_list = []
        self._control_param_list = []
        self._subckt_directive_param_list = []
        self._subckt_device_param_list = []
        self._initial_conditions_list = []
        self._comment = None
        self._flag_control_device = False
        self._error_type = ""
        self._error_message = ""
        self._unknown_nodes = []
        self._m_param = None
        self._source_params = {}
        self._preprocess_keyword_value = []
        self._flag_unresolved_device = False
        self._flag_top_pnl = False
        self._model_def_scope = ""

    def __str__(self):
        return_string = "*********Parsed Netlist*********\n"
        return_string += "Type: " + str(self._type) + "\n"
        return_string += "Local Type: " + str(self._local_type) + "\n"
        return_string += "Name: " + str(self._name) + "\n"
        return_string += "Filename: " + str(self._filename) + "\n"
        return_string += "Linenum: " + str(self._linenum) + "\n"
        return_string += "Params Dict: " + str(self._params_dict) + "\n"
        return_string += "Known Objs: " + str(self._known_objects) + "\n"
        return_string += "Lazy Sts: " + str(self._lazy_statements) + "\n"
        return_string += "Trans vals: " + str(self._transient_values) + "\n"
        return_string += "Meas Dict: " + str(self._meas_dict) + "\n"
        return_string += "Output var vals: " + str(self._output_variable_values) + "\n"
        return_string += "Func Args: " + str(self._func_arg_list) + "\n"
        return_string += "Val List: " + str(self._value_list) + "\n"
        return_string += "Sweep Params List: " + str(self._sweep_param_list) + "\n"
        return_string += "Schedule Params List: " + str(self._schedule_param_list) + "\n"
        return_string += "Table Params List: " + str(self._table_param_list) + "\n"
        return_string += "Poly Params List: " + str(self._poly_param_list) + "\n"
        return_string += "Control Params List: " + str(self._control_param_list) + "\n"
        return_string += "Subckt Dir Param List: " + str(self._subckt_directive_param_list) + "\n"
        return_string += "Subckt Dev Param List: " + str(self._subckt_device_param_list) + "\n"
        return_string += "Initial Conditions List: " + str(self._initial_conditions_list) + "\n"
        return_string += "Comment: " + str(self._comment) + "\n"
        return_string += "Flag Control: " + str(self._flag_control_device) + "\n"
        return_string += "Error Type: " + str(self._error_type) + "\n"
        return_string += "Error Message: " + str(self._error_message) + "\n"
        return_string += "Unknown nodes: " + str(self._unknown_nodes) + "\n"
        return_string += "M param: " + str(self._m_param) + "\n"
        return_string += "Preprocess Keyword Value: " + str(self._preprocess_keyword_value) + "\n"
        return_string += "Flag Unresolved Device: " + str(self._flag_unresolved_device) + "\n"
        return_string += "Flag Top PNL: " + str(self._flag_top_pnl) + "\n"
        return_string += "Model Definition Scope: " + str(self._model_def_scope) + "\n"
        return_string += "**********************************"

        return return_string

    @property
    def func_arg_list(self):
        return self._func_arg_list

    @property
    def schedule_param_list(self):
        return self._schedule_param_list

    @property
    def poly_param_list(self):
        return self._poly_param_list

    @property
    def table_param_list(self):
        return self._table_param_list

    @property
    def control_param_list(self):
        return self._control_param_list

    @property
    def subckt_directive_param_list(self):
        return self._subckt_directive_param_list

    @property
    def subckt_device_param_list(self):
        return self._subckt_device_param_list

    @subckt_device_param_list.setter
    def subckt_device_param_list(self, x):
        self._subckt_device_param_list = x

    @property
    def initial_conditions_list(self):
        return self._initial_conditions_list

    @property
    def lazy_statements(self):
        return self._lazy_statements

    @property
    def source_params(self):
        return self._source_params

    @property
    def comment(self):
        return self._comment

    @property
    def flag_control_device(self):
        return self._flag_control_device

    @flag_control_device.setter
    def flag_control_device(self, x):
        self._flag_control_device = x

    @property
    def flag_unresolved_device(self):
        return self._flag_unresolved_device

    @flag_unresolved_device.setter
    def flag_unresolved_device(self, x):
        self._flag_unresolved_device = x

    @property
    def flag_top_pnl(self):
        return self._flag_top_pnl

    @flag_top_pnl.setter
    def flag_top_pnl(self, x):
        self._flag_top_pnl = x

    @property
    def model_def_scope(self):
        return self._model_def_scope

    @model_def_scope.setter
    def model_def_scope(self, x):
        self._model_def_scope = x

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, typ):
        self._type = typ

    @property
    def local_type(self):
        return self._local_type

    @local_type.setter
    def local_type(self, typ):
        self._local_type = typ

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename):
        self._filename = filename

    @property
    def linenum(self):
        return self._linenum

    @property
    def known_objects(self):
        return self._known_objects

    @property
    def value_list(self):
        return self._value_list

    @property
    def sweep_param_list(self):
        return self._sweep_param_list

    @property
    def error_type(self):
        return self._error_type

    @error_type.setter
    def error_type(self, strvalue):
        self._error_type = strvalue

    @property
    def error_message(self):
        return self._error_message

    @error_message.setter
    def error_message(self, strvalue):
        self._error_message = strvalue

    def add_sweep_param_value(self, value):
        self._sweep_param_list.append(value)

    def add_table_param_value(self, value):
        self._table_param_list.append(value)

    def add_poly_param_value(self, value):
        self._poly_param_list.append(value)

    def add_control_param_value(self, value):
        self._control_param_list.append(value)

    def add_schedule_param_value(self, value):
        self._schedule_param_list.append(value)

    def add_subckt_directive_param_value(self, value):
        self._subckt_directive_param_list.append(value)

    def add_subckt_device_param_value(self, value):
        self._subckt_device_param_list.append(value)

    def add_param_value_pair(self, param_name, param_val):
        self._params_dict[param_name] = param_val

    def add_known_object(self, obj_name, obj_type):
        self._known_objects[obj_type] = obj_name

    def add_lazy_statement(self, obj_name, obj_types):
        self._lazy_statements[obj_name] = obj_types

    def add_transient_value(self, trans_value):
        self._transient_values.append(trans_value)

    def add_meas_analysis_condition(self, meas_analysis_condition):
        self._meas_dict[meas_analysis_condition] = OrderedDict()

    def add_meas_param_value_pair(self, meas_analysis_condition, meas_param_name, meas_param_val):
        self._meas_dict[meas_analysis_condition][meas_param_name] = meas_param_val

    def add_output_variable_value(self, outvar_value):
        self._output_variable_values.append(outvar_value)

    def add_func_arg_value(self, arg_value):
        self._func_arg_list.append(arg_value)

    def add_value_to_value_list(self, value):
        self._value_list.append(value)

    @property
    def m_param(self):
        return self._m_param

    @m_param.setter
    def m_param(self, value):
        self._m_param = value

    @property
    def params_dict(self):
        return self._params_dict

    @params_dict.setter
    def params_dict(self, x):
        self._params_dict = x

    @property
    def transient_values(self):
        return self._transient_values

    @property
    def meas_dict(self):
        return self._meas_dict

    @meas_dict.setter
    def meas_dict(self, x):
        self._meas_dict = x

    @property
    def output_variable_values(self):
        return self._output_variable_values

    def add_inline_comment(self, comment_string):
        self._comment = comment_string

    def add_comment(self, comment_string):
        self._params_dict[Types.comment] = comment_string

    def add_unknown_node(self, unknown_node):
        self._unknown_nodes.append(unknown_node)

    def add_preprocess_keyword_value(self, preprocess_keyword_value_string):
        self._preprocess_keyword_value.append(preprocess_keyword_value_string)

    @property
    def unknown_nodes(self):
        return self._unknown_nodes

    @unknown_nodes.setter
    def unknown_nodes(self, x):
        self._unknown_nodes = x

    @property
    def preprocess_keyword_value(self):
        return self._preprocess_keyword_value
