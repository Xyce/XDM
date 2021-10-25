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
import os
import re

from xdm import Types
from xdm.statements.nodes.devices import Device
from xdm.statements.commands import Command


def append(c, obj, d, lang, delimiter=' '):
    return_string = ''

    for t in c.value:
        v = eval(t.ref)(t, obj, d, lang)
        if v is not None:
            return_string += v

    return return_string


def string(c, obj, d, lang, delimiter=' '):
    return c.value


def value(c, obj, d, lang, delimiter=' '):
    v = 'Types.'.strip() + c.label.strip()
    if eval(v) in obj.props:
        if isinstance(obj.props[eval(v)], str):
            return obj.props[eval(v)]
        elif not obj.props[eval(v)]:
            return ''
        else:
            # if instance of a .MODEL, and the model is binned, only take root name
            if "." in obj.props[eval(v)].name:
                return obj.props[eval(v)].name.split(".")[0]
            return obj.props[eval(v)].name

    return ''


def scopedNode(c, obj, d, lang, delimiter=' '):
    v = 'Types.'.strip() + c.label.strip()
    if eval(v) in obj.props:
        if isinstance(obj.props[eval(v)], list):
            scoped_string = obj.props[eval(v)][:-1].join(":")
            scoped_string += ":" + obj.props[eval(v)][:-1].name
        if isinstance(obj.props[eval(v)], str):
            return obj.props[eval(v)]
        else:
            return obj.props[eval(v)].name

    return ''


def bracketedValue(c, obj, d, lang, delimiter=' '):
    v = 'Types.'.strip() + c.label.strip()
    if eval(v) in obj.props:
        if isinstance(obj.props[eval(v)], str):
            return '[' + obj.props[eval(v)] + ']'
        else:
            return '[' + obj.props[eval(v)].name + ']'

    return ''


def pair(c, obj, d, lang, delimiter=' '):
    PAIR_JOIN = '='

    return_string = ''

    # need to resolve exclude list Types. and include list bare parameters
    exclude_list = map(lambda x: eval('Types.' + x.strip()), c.exclude_list)
    exclude_list.append(Types.statementType)
    include_list = c.include_list

    cur_length = 0

    if len(c.include_list) == 0:
        for prop in obj.props:
            if prop not in exclude_list:
                len_this = len(prop + PAIR_JOIN + obj.props[prop] + delimiter)
                if cur_length > 0 and cur_length + len_this > 80:
                    return_string += '\n+ '
                    cur_length = 0
                return_string += (prop + PAIR_JOIN + obj.props[prop] + delimiter)
                cur_length += len_this
    else:
        for prop in c.include_list:
            if obj.props.get(prop):
                len_this = len(prop + PAIR_JOIN + obj.props[prop] + delimiter)
                if cur_length > 0 and cur_length + len_this > 80:
                    return_string += '\n+ '
                    cur_length = 0
                return_string += (prop + PAIR_JOIN + obj.props[prop] + delimiter)
                cur_length += len_this

    return return_string.strip()


def params(c, obj, d, lang, delimiter=' '):
    PARAMS_JOIN = '='

    return_string = ''

    cur_length = 0

    for param in obj.params:
        key_param = lang.key_params.get(param)
        if not key_param:
            local_param_name = param
            logging.debug("From file '" + str(os.path.basename(obj.file)) + "' line: " + str(obj.line_num)
                          + " Writing param that does not exist in target language: "
                          + str(param) + " \n")
        else:
            local_param_name = key_param.label
        local_param_value = obj.params[param]
        len_this = len(local_param_name + PARAMS_JOIN + local_param_value + delimiter)
        if cur_length > 0 and cur_length + len_this > 80:
            return_string += '\n+ '
            cur_length = 0
        return_string += (local_param_name + PARAMS_JOIN + local_param_value + delimiter)
        cur_length += len_this

    return return_string.strip()


def portParams(c, obj, d, lang, delimiter=' '):
    PORT_PARAMS = ["DC", "PORT", "Z0", "AC"]

    return_string = ''

    cur_length = 0

    for param in PORT_PARAMS:
        if param in obj.params:
            PARAMS_JOIN = ' '
            key_param = lang.key_params.get(param)
            if not key_param:
                local_param_name = param
                logging.debug("From file '" + str(os.path.basename(obj.file)) + "' line: " + str(obj.line_num)
                              + " Writing param that does not exist in target language: "
                              + str(param) + " \n")
            else:
                local_param_name = key_param.label
            if local_param_name in ["Z0", "PORT"]:
                PARAMS_JOIN = '='
            local_param_value = obj.params[param]
            len_this = len(local_param_name + PARAMS_JOIN + local_param_value + delimiter)
            if cur_length > 0 and cur_length + len_this > 80:
                return_string += '\n+ '
                cur_length = 0
            return_string += (local_param_name + PARAMS_JOIN + local_param_value + delimiter)
            cur_length += len_this

    return return_string.strip()


def controlDeviceValue(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if Types.controlDeviceValue in obj.props:
        return_string += (obj.props[Types.controlDeviceValue].device_type + obj.props[Types.controlDeviceValue].name)

    return return_string


def controlDeviceList(c, obj, d, lang, delimiter=' '):
    v = 'Types.'.strip() + c.label.strip()

    return_string = ''

    if eval(v) in obj.props:
        if isinstance(obj.props[eval(v)], list):
            for device in obj.props[eval(v)]:
                return_string += (device.device_type + device.name + delimiter)
        elif isinstance(obj.props[eval(v)], Device):
            return_string = obj.props[eval(v)].name

    return return_string.strip()


def transient(c, obj, d, lang, delimiter=' '):
    v = 'Types.'.strip() + c.label.strip()
    if eval(v) in obj.props:
        return obj.props[eval(v)].spice_string()
    return ''


def scheduleValue(c, obj, d, lang, delimiter=' '):
    v = 'Types.'.strip() + c.label.strip()
    if eval(v) in obj.props:
        return obj.props[eval(v)].spice_string()
    return ''


def acValue(c, obj, d, lang, delimiter=' '):
    v = 'Types.'.strip() + c.label.strip()
    if eval(v) in obj.props:
        return obj.props[eval(v)].spice_string()
    return ''


def dcValue(c, obj, d, lang, delimiter=' '):
    v = 'Types.'.strip() + c.label.strip()
    if eval(v) in obj.props:
        return obj.props[eval(v)].spice_string()
    return ''


def valueExpression(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if obj.props.get(Types.valueExpression):
        return_string += 'VALUE'
        return_string += '='
        return_string += replace_inner_curly_braces(obj.props[Types.valueExpression])
    return return_string


def controlExpression(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if obj.props.get(Types.controlExpression):
        return_string += 'CONTROL'
        return_string += '='
        return_string += replace_inner_curly_braces(obj.props[Types.controlExpression])
    return return_string


def tableExpression(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if Types.tableExpression in obj.props:
        return obj.props[Types.tableExpression].spice_string()
    return ''


def polyExpression(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if Types.polyExpression in obj.props:
        return obj.props[Types.polyExpression].spice_string()
    return return_string


def measurementTypeValue(c, obj, d, lang, delimiter=' '):
    v = 'Types.'.strip() + c.label.strip()
    if eval(v) in obj.props:
        return obj.props[eval(v)].spice_string()
    return ''


def specialValue(c, obj, d, lang, delimiter=' '):
    return_string = ''
    v = 'Types.'.strip() + c.label.strip()
    if eval(v) in obj.props:
        return_string = obj.props[eval(v)]
    return return_string


def voltageExpression(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if obj.props.get(Types.voltage):
        return_string += 'V='
        if obj.props.get(Types.tableExpression):
            expression = tableExpression(c, obj, d, lang)
        else:
            expression = obj.props[Types.expression]
        if len(expression) > 0 and expression[0] != '{' and expression[-1] != '}':
            expression = '{' + expression + '}'
        return_string += expression
    return return_string


def currentExpression(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if obj.props.get(Types.current):
        return_string += 'I='
        if obj.props.get(Types.tableExpression):
            expression = tableExpression(c, obj, d)
        else:
            expression = obj.props[Types.expression]
        if len(expression) > 0 and expression[0] != '{' and expression[-1] != '}':
            expression = '{' + expression + '}'
        return_string += expression
    return return_string


def subcircuitParamsList(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if obj.props.get(Types.subcircuitParamsList):
        param_dict = obj.props[Types.subcircuitParamsList]
        return_string += 'PARAMS:'
        return_string += delimiter
        for param in param_dict:
            if "\n" in return_string:
                tmpString = return_string.split("\n")
                if len(tmpString[-1]) > 80:
                    return_string += "\n+ "
            elif len(return_string) > 80:
                return_string += "\n+ "
            return_string += param
            return_string += '='
            return_string += param_dict[param]
            return_string += delimiter
    return return_string.strip()


def paramsList(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if obj.props.get(Types.paramsList):
        param_dict = obj.props[Types.paramsList]
        for param in param_dict:
            if "\n" in return_string:
                tmpString = return_string.split("\n")
                if len(tmpString[-1]) > 80:
                    return_string += "\n+ "
            elif len(return_string) > 80:
                return_string += "\n+ "
            return_string += param
            return_string += '='
            return_string += param_dict[param]
            return_string += delimiter
    return return_string.strip()


def nodeList(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if obj.props.get(Types.nodeList):
        for node in obj.props[Types.nodeList]:
            return_string += node.name
            return_string += delimiter
    return return_string.strip()


def interfaceNodeList(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if obj.props.get(Types.interfaceNodeList):
        for node in obj.props[Types.interfaceNodeList]:
            return_string += node.name
            return_string += delimiter
    return return_string.strip()


def outputVariableList(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if obj.props.get(Types.outputVariableList):
        for variable in obj.props[Types.outputVariableList]:
            return_string += variable
            return_string += delimiter
    return return_string.strip()


def initialConditionsList(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if obj.props.get(Types.initialConditionsList):
        for initial_condition in obj.props[Types.initialConditionsList]:
            return_string += initial_condition.ic_type.upper()
            return_string += '('
            return_string += initial_condition.ic_node.name
            return_string += ')='
            return_string += initial_condition.ic_value
            return_string += delimiter
    return return_string.strip()


def optionPackageTypeValue(c, obj, d, lang, delimiter=' '):
    return_string = ''
    return return_string.strip()


def sweep(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if obj.props.get(Types.sweep):
        return_string += obj.props[Types.sweep].spice_string(delimiter)
    return return_string.strip()


def valueList(c, obj, d, lang, delimiter=' '):
    v = 'Types.'.strip() + c.label.strip()
    return_string = ''
    if eval(v) in obj.props:
        for value in obj.props[eval(v)]:
            return_string += value
            return_string += delimiter
    return return_string.strip()


def dataList(c, obj, d, lang, delimiter=' '):
    v = 'Types.'.strip() + c.label.strip()
    return_string = '\n+'
    if eval(v) in obj.props:
        for value in obj.props[eval(v)]:
            return_string += ' '+value
    return return_string


def funcArgList(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if obj.props.get(Types.funcArgList):
        return_string += ",".join(obj.props[Types.funcArgList])
    return return_string.strip()


def funcExpression(c, obj, d, lang, delimiter=' '):
    return_string = ''
    if obj.props.get(Types.funcExpression):
        return_string += obj.props[Types.funcExpression]
    return return_string.strip()


# private
def model_level(c, obj, d, lang, delimiter=' '):
    return_string = ''
    return_string += "LEVEL"
    return_string += "="
    return_string += c.value
    return return_string.strip()


def handle_inline_comment(ws, inline_comment_tokens, lang):
    return_string = ' '
    if ws.inline_comment:
        for field in inline_comment_tokens:
            try:
                r = eval(field.ref)(field, ws, inline_comment_tokens, lang)
                return_string += r
                
            except AttributeError as e:
                logging.error('Inline comment at ' + str(ws.line_num[0]) + ' : ' + str(ws) + ' Field: ' + str(field) + ' gave: ' + e.message)
                raise Exception('*****FATAL ERROR*****')

        return_string += ws.inline_comment.strip()
    return return_string


def replace_inner_curly_braces(expression):
    return_expression = expression.strip()
    if len(return_expression) > 1 and return_expression[0] == '{' and return_expression[-1] == '}':
        inner_expression = return_expression[1:-1]
        inner_expression = inner_expression.replace('{', '(')
        inner_expression = inner_expression.replace('}', ')')
        return_expression = '{' + inner_expression + '}'
    return return_expression

def setup_special_variable_dicts(in_admin_writer, out_admin_writer):

    target_lang_conflict_dict = {}
    source_lang_specials_dict = {}
    for in_token, out_token in zip(in_admin_writer.token_list, out_admin_writer.token_list):
        # dict to store variable (out_token.value) that conflicts with a special variable 
        # in target lang. The in_token.value is the corresponding special variable in the
        # source lang - only stored just in case for now, not used.
        if out_token.ref == "string" and out_token.value and in_token.value != out_token.value:
            target_lang_conflict_dict[out_token.value] = in_token.value

        # dict to store special variables in source lang
        if in_token.ref == "string" and in_token.value:
            source_lang_specials_dict[in_token.value] = out_token.value

    return target_lang_conflict_dict, source_lang_specials_dict

def handle_special_variables(ws, target_lang_conflict_dict, source_lang_specials_dict, in_admin_writer, out_admin_writer):
    convBool = True
    master_convBool = True
    unsupported_var = ""
    conflicting_var = []
    master_conflicting_var = []

    if ws.params:
        for key in ws.params:
            item = ws.params[key]
            if item is not None:
                convBool, unsupported_var, conflicting_var, ret_item = token_conversion(item, target_lang_conflict_dict, source_lang_specials_dict)
                if not convBool:
                    if unsupported_var:
                        return convBool, unsupported_var, conflicting_var
                    elif conflicting_var:
                        master_convBool = False
                        for var in conflicting_var:
                            master_conflicting_var.append(var)
            else:
                ret_item = item
            ws.params[key] = ret_item

    for key in ws.props:
        if key == "OUTPUTVARIABLE_LIST":
            for ind,item in enumerate(ws.props[key]):
                convBool, unsupported_var, conflicting_var, ret_item = token_conversion(item, target_lang_conflict_dict, source_lang_specials_dict)
                if not convBool:
                    if unsupported_var:
                        return convBool, unsupported_var, conflicting_var
                    elif conflicting_var:
                        master_convBool = False
                        for var in conflicting_var:
                            master_conflicting_var.append(var)
                ws.props[key][ind] = ret_item
        elif key == "FUNC_EXPRESSION" or key == "FUNC_NAME_VALUE":
                item = ws.props[key]
                convBool, unsupported_var, conflicting_var, ret_item = token_conversion(item, target_lang_conflict_dict, source_lang_specials_dict)
                if not convBool:
                    if unsupported_var:
                        return convBool, unsupported_var, conflicting_var
                    elif conflicting_var:
                        master_convBool = False
                        for var in conflicting_var:
                            master_conflicting_var.append(var)
                ws.props[key] = ret_item
        elif key == "PARAMS_LIST" or key == "SUBCIRCUIT_PARAMS_LIST":
            for param_key in ws.props[key]:
                # check param name is not a reserved special variable
                convBool, unsupported_var, conflicting_var, ret_item = token_conversion(param_key, target_lang_conflict_dict, source_lang_specials_dict)
                if not convBool:
                    if unsupported_var:
                        return convBool, unsupported_var, conflicting_var
                    elif conflicting_var:
                        master_convBool = False
                        for var in conflicting_var:
                            master_conflicting_var.append(var)
                
                # check param doesn't use a reserved special variable
                item = ws.props[key][param_key]
                convBool, unsupported_var, conflicting_var, ret_item = token_conversion(item, target_lang_conflict_dict, source_lang_specials_dict)
                if not convBool:
                    if unsupported_var:
                        return convBool, unsupported_var, conflicting_var
                    elif conflicting_var:
                        master_convBool = False
                        for var in conflicting_var:
                            master_conflicting_var.append(var)
                ws.props[key][param_key] = ret_item

                # map to the correct command in target lang (i.e., XYCE needs .GLOBAL_PARAM for special variables)
                if isinstance(ws, Command) and ret_item != item:
                    for in_token, out_token in zip(in_admin_writer['specialvariables'].token_list, out_admin_writer['specialvariables'].token_list):
                        if in_token.ref == "command" and ws.command_type.upper() == in_token.value.upper():
                            ws.command_type = out_token.value

    return master_convBool, unsupported_var, master_conflicting_var

def handle_output_variables(ws, target_lang_conflict_dict, source_lang_specials_dict):
    convBool = True
    unsupported_vars = []

    for key in ws.props:
        if key == "OUTPUTVARIABLE_LIST":
            for ind,item in enumerate(ws.props[key]):
                convBool, unsupported_var, conflicting_var, ret_item = token_conversion(item, target_lang_conflict_dict, source_lang_specials_dict)
                if not convBool:
                    if unsupported_var:
                        unsupported_vars.append(unsupported_var)
                    elif conflicting_var: 
                        ws.props[key] = ret_item

    if unsupported_vars:
        convBool = False
    else:
        convBool = True

    return convBool, unsupported_vars

def token_conversion(item, target_lang_conflict_dict, source_lang_specials_dict):
    item_fields = re.split("(\*|/|\+|-|\(|\)| |'|\[|\]|\{|\})", item)
    converted_item_fields = []
    convBool = True
    master_convBool = True
    unsupported_var = ""
    conflicting_var = []

    for item_field in item_fields:
        converted_item_field = item_field
        item_field_lower = item_field.lower()

        # check if variable conflicts with a special variable in target lang
        if item_field_lower in target_lang_conflict_dict:
            master_convBool = False
            conflicting_var.append(item_field)
            # return convBool, unsupported_var, conflicting_var, item

            # Dirty hack to rename variables that conflict in name with special variables in Xyce.
            # may need to remove someday and return to original code above
            converted_item_field = "XYCE_"+item_field_lower

        # check if variable is a special variable in source lang
        if item_field_lower in source_lang_specials_dict:
            # check if special variable has valid counterpart in target lang
            if source_lang_specials_dict[item_field_lower] == "":
                convBool = False
                unsupported_var = item_field
                return convBool, unsupported_var, conflicting_var, item

            converted_item_field = source_lang_specials_dict[item_field_lower]

        converted_item_fields.append(converted_item_field)

    converted_item = ''.join(converted_item_fields)
    return master_convBool, unsupported_var, conflicting_var, converted_item
