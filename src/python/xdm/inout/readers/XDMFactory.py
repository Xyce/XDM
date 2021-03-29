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


import itertools
import logging
import os
from collections import deque

import xdm.Types as Types
from xdm.exceptions import *
from xdm.inout.readers.ParsedNetlistLine import ParsedNetlistLine
from xdm.statements.commands import *
from xdm.statements.nodes import *
from xdm.statements.nodes.devices import *
from xdm.statements.nodes.models import MASTER_MODEL
from xdm.statements.nodes.models.modeldefs import *
from xdm.statements.refs import *
from xdm.statements.structures import *
from xdm.statements.structures.SWEEP import *

supported_devices = ["B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "J", "M", "O", "P", "Q", "R", "S", "T", "V", "X", "W",
                     "Y", "YPDE", "YROM", "YACC", "Z", "SW"]

supported_directives = [".AC", ".DC", ".FOUR", ".HB", ".MEASURE", ".OP", ".SENS", ".STEP", ".TRAN", ".DCVOLT", ".FUNC",
                        ".GLOBAL", ".GLOBAL_PARAM", ".IC", ".OPTIONS", ".PARAM", ".PREPROCESS", ".PRINT", ".SAVE", ".ENDS",
                        ".END", ".SUBCKT", ".NODESET", ".TEMP", ".PROBE", ".ENDL", ".ALIASES", ".AUTOCONVERGE", ".DISTRIBUTION",
                        ".ENDALIASES", ".LOADBIAS", ".MC", ".NOISE", ".PLOT", ".SAVEBIAS", ".STIMULUS", ".TEXT", ".TF",
                        ".VECTOR", ".WATCH", ".WCASE", ".TR", ".INITCOND", ".MOR", ".MPDE", ".PROBE64", "ac", "alter",
                        "altergroup", "check", "checklimit", "cosim", "dc", "dcmatch", "envlp", "hb", "hbac", "hbnoise",
                        "hbsp", "info", "loadpull", "montecarlo", "noise", "options", "pac", "pdisto", "pnoise", "psp",
                        "pss", "pstb", "pxf", "pz", "qpac", "qpnoise", "qpsp", "qpss", "qpxf", "reliability", "set",
                        "shell", "sp", "stb", "sweep", "tdr", "tran", "uti", "xf", "analogmodel", "bsource",
                        "checkpoint", "smiconfig", "constants", "convergence", "encryption", "expressions", "functions",
                        "global", "ibis", "ic", "if", "keywords", "memory", "nodeset", "param_limits", "paramset",
                        "rfmemory", "save", "savestate", "sens", "spectrerf", "stitch", "vector", "veriloga", "library",
                        "endlibrary", "modelParameter", "simulatorOptions", "finalTimeOP", "element", "outputParameter",
                        "designParamVals", "primitives", "subckts", "saveOptions", ".LIN", ".MACRO", ".EOM", ".DATA",
                        ".ENDDATA"]

model_map_dict = {"CORE": "K", "DIG": "Y", "NPN": "Q", "PNP": "Q", "NJF": "J", "PJF": "J", "NMF": "Z", "PMF": "Z",
                  "NMOS": "M", "PMOS": "M", "VSWITCH": "S", "ISWITCH": "W", "LTRA": "O", "RXN": "Y", "SWITCH": "SW",
                  "ZOD": "YPDE", "NEURONPOP": "Y", "NEURON": "Y", "SYNAPSE": "Y", "XYGRA": "Y"}

generic_map_dict = {Types.value: str,
                    Types.modelName: MASTER_MODEL,
                    Types.generalNodeName: ENODE
                    }


def build_node(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    try:
        node_type = eval('Types.' + label.strip())
    except:
        node_type = None
        logging.warning("Line(s):" + str(
            parsed_netlist_line.linenum) + ". No node type defined in Types: " + label + ", from XML definition")
    node_name = parsed_netlist_line.known_objects.get(node_type)
    if node_name:
        node = reader_state.scope_index.get_object("__ENODE__" + node_name)
        # check if ground node synonyms are present. 
        # if so, put into parsed netlist line object preprocess directive
        if node_name.lower() in ["gnd", "gnd!", "ground"]:
            # check to make sure ground node synonym is not one of the subcircuit's interface
            # nodes. if it is, do not add the preprocess directive
            is_interface_node = False
            if reader_state.scope_index.subckt_command:
                for interface_node in reader_state.scope_index.subckt_command.props["INTERFACE_NODE_LIST"]:
                    if node_name == interface_node.name:
                        is_interface_node = True
                        break

            if not "REPLACEGROUND TRUE" in parsed_netlist_line.preprocess_keyword_value and not is_interface_node:
                parsed_netlist_line.add_preprocess_keyword_value("REPLACEGROUND TRUE")
        if node is None:
            node = ENODE(node_name, reader_state.scope_index.uid_index.uid)
            reader_state.scope_index.add(node, case_insensitive=reader_state.is_case_insensitive())
        props[node_type] = node


def handle_value(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    try:
        types_label = eval('Types.' + label.strip())
        props[types_label] = parsed_netlist_line.known_objects.get(types_label)
        return
    except:
        pass

    # conversion of param to prop
    label_param = language_device_type.get_prop(label)
    if label_param:
        label_key = label_param.label_key
        try:
            types_label = eval('Types.' + label_key.strip())
            if parsed_netlist_line.params_dict.get(label):
                props[types_label] = parsed_netlist_line.params_dict[label]
            return
        except:
            pass

    # write in logic to figure out what the default value is and see if it's different
    # if not different from default, don't write in?

    if parsed_netlist_line.params_dict.get(label):
        label_local = label
        label_value = parsed_netlist_line.params_dict[label]
        try:
            label_key = language_device_type.get_param(label_local).label_key
            props[label_key] = label_value
            del parsed_netlist_line.params_dict[label_local]
        except:
            logging.info("Could not find param type in XML definition: " + label_local)
            logging.info("for type " + language_device_type.identity())


def handle_sub_dir_node_list(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    # exclusively for subcircuit device
    node_list = []
    for key in list(parsed_netlist_line.subckt_device_param_list)[:-1]:
        node_list.append(build_node_by_value(parsed_netlist_line, key, reader_state))
    props[Types.node_list] = node_list


def handle_subcircuit_name_value(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    # exclusively for subcircuit device
    name = list(parsed_netlist_line.subckt_device_param_list)[-1]
    subckt_dir_name = reader_state.scope_index.get_object(name)

    if subckt_dir_name is None:
        props[Types.subcircuitNameValue] = reader_state.scope_index.add_lazy_statement(name,
                                                                                       reader_state.scope_index.uid_index.uid)
    elif subckt_dir_name.get_prop(Types.directiveName) == ".SUBCKT" or isinstance(subckt_dir_name, LAZY_STATEMENT):
        props[Types.subcircuitNameValue] = subckt_dir_name
    elif subckt_dir_name is not None and not isinstance(subckt_dir_name, LAZY_STATEMENT):
        raise InvalidTypeException(name + "is not of type SUBCKT, but of type: " + subckt_dir_name.__class__)


def handle_subcircuit_params_list(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    if len(parsed_netlist_line.params_dict) > 0:
        props[Types.subcircuitParamsList] = parsed_netlist_line.params_dict


def build_value_list(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    if len(parsed_netlist_line.value_list) > 0:
        props[Types.valueList] = parsed_netlist_line.value_list


def build_file_name(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    if parsed_netlist_line.known_objects.get(Types.fileNameValue):
        props[Types.fileNameValue] = parsed_netlist_line.known_objects.get(Types.fileNameValue)


def build_lib_entry(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    if parsed_netlist_line.known_objects.get(Types.libEntry):
        props[Types.libEntry] = parsed_netlist_line.known_objects.get(Types.libEntry)


def build_opt_pack_type_value(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    pkgValue = parsed_netlist_line.known_objects.get(Types.optionPkgTypeValue).upper()
    props[Types.optionPkgTypeValue] = pkgValue
    tempParamsDict = {}

    for prop in language_device_type.nested_prop_dict.get(pkgValue):
        prop_value = parsed_netlist_line.params_dict.get(prop.label)
        if prop_value:
            tempParamsDict[prop.label] = prop_value
    parsed_netlist_line.params_dict = tempParamsDict


def build_schedule_value(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    if parsed_netlist_line.known_objects.get(Types.scheduleType):
        schedule = SCHEDULE()
        schedule_pairs = convert_list_to_list_of_pairs(parsed_netlist_line.schedule_param_list)
        for schedule_pair in schedule_pairs:
            schedule.add_time_max_step_pair(schedule_pair[0], schedule_pair[1])
        props[Types.scheduleValue] = schedule


def build_output_variable_list(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    props[Types.outputVariableList] = parsed_netlist_line.output_variable_values


def build_initial_conditions_list(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    props[Types.initialConditionsList] = []

    for ic_dict in parsed_netlist_line.initial_conditions_list:
        synth_prop = {}
        synth_pnl = ParsedNetlistLine(parsed_netlist_line.filename, parsed_netlist_line.linenum)
        synth_pnl.add_known_object(ic_dict[Types.generalNodeName], Types.generalNodeName)
        build_node(synth_pnl, reader_state, language_device_type, synth_prop, "generalNodeName", value)
        ic = IC(ic_dict[Types.voltageOrCurrent], synth_prop[Types.generalNodeName], ic_dict[Types.generalValue])

        props[Types.initialConditionsList].append(ic)


def build_func_arg_list(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    props[Types.funcArgList] = parsed_netlist_line.func_arg_list


def build_func_expression(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    if parsed_netlist_line.known_objects.get(Types.funcExpression):
        props[Types.funcExpression] = parsed_netlist_line.known_objects[Types.funcExpression]


def build_subckt_name(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    props[Types.name] = parsed_netlist_line.name


def handle_node_list(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    node_list = []
    for node_string in parsed_netlist_line.subckt_directive_param_list:
        node_list.append(build_node_by_value(parsed_netlist_line, node_string, reader_state))

    props[Types.node_list] = node_list


def handle_interface_node_list(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    node_list = []

    for node_string in parsed_netlist_line.subckt_directive_param_list:
        node_list.append(INTERFACENODE(node_string, reader_state.scope_index.uid_index.uid))

    props[Types.interfaceNodeList] = node_list


def build_name(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    # device_type = parsed_netlist_line.type
    # device_name = device_type + parsed_netlist_line.name
    # props[Types.name] = device_name
    props[Types.name] = parsed_netlist_line.name


def build_model_name(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    pass


def handle_control_type(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    if label == "current" or label == "voltage":
        props[Types.controlType] = label
    else:
        logging.warning("Line(s):" + str(
            parsed_netlist_line.linenum) + ". From XML, device control type must be 'current' or 'voltage', but is: " + label)


def handle_control_device_value(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    if len(parsed_netlist_line.control_param_list) > 0:
        control_device_string = parsed_netlist_line.control_param_list[0]

        if len(parsed_netlist_line.control_param_list) > 1:
            logging.warning("Line(s):" + str(
                parsed_netlist_line.linenum) + ". XML controlDeviceValue took one value from PNL value list. Consider using controlDeviceList.  Remaining list: " + str(
                parsed_netlist_line.control_param_list[1:]))

        props[Types.controlDeviceValue] = control_device_string
        # this triggers post-processing to enable the device string to be converted to a device object
        parsed_netlist_line.flag_control_device = True


def handle_control_device_list(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    control_device_list = []
    for deviceId in parsed_netlist_line.control_param_list:
        # device = reader_state.scope_index.get_object("__DEVICE__" + deviceId)
        # if None == device:
        #     device = reader_state.scope_index.add_lazy_statement(deviceId, reader_state.scope_index.uid_index.uid)
        # control_device_list.append(device)
        control_device_list.append(deviceId)
    if len(control_device_list) > 0:
        parsed_netlist_line.flag_control_device = True

    # need to handle controlDeviceList binding to objects elsewhere
    props[Types.controlDeviceList] = control_device_list


def build_value_expression(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    if Types.valueKeyword in parsed_netlist_line.known_objects:
        value = build_value_prop(parsed_netlist_line, Types.expression)
        del parsed_netlist_line.known_objects[Types.valueKeyword]
        del parsed_netlist_line.known_objects[Types.expression]
        props[Types.valueExpression] = value


def build_table_expression(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    if Types.table in parsed_netlist_line.known_objects:
        table_expression = build_value_prop(parsed_netlist_line, Types.expression)
        table_pairs = convert_list_to_list_of_pairs(parsed_netlist_line.table_param_list)
        del parsed_netlist_line.known_objects[Types.table]
        del parsed_netlist_line.known_objects[Types.expression]
        props[Types.tableExpression] = TABLE(table_expression, table_pairs)


def convert_list_to_list_of_pairs(list):
    return zip(list[::2], list[1::2])


def build_poly_expression(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    control_type = props.get(Types.controlType)
    if control_type == "voltage":
        handleVoltageControlledPoly(parsed_netlist_line, props, reader_state)
    elif control_type == "current":
        handleCurrentControlledPoly(parsed_netlist_line, props, reader_state)
    else:
        # TODO: Fix this so order does not matter in XML
        logging.warn("Line(s):" + str(
            parsed_netlist_line.linenum) + ". Control type not set. It must be defined in the XML device prior to polyExpression.")


def build_voltage_expression(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    # clean up
    if Types.voltage in parsed_netlist_line.known_objects:
        props[Types.voltage] = parsed_netlist_line.known_objects[Types.voltage]
    if Types.expression in parsed_netlist_line.known_objects:
        if parsed_netlist_line.known_objects.get(Types.table):
            build_table_expression(parsed_netlist_line, reader_state, language_device_type, props, label, value)
        else:
            props[Types.expression] = parsed_netlist_line.known_objects[Types.expression]


def build_current_expression(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    # clean up
    if Types.current in parsed_netlist_line.known_objects:
        props[Types.current] = parsed_netlist_line.known_objects[Types.current]
    if Types.expression in parsed_netlist_line.known_objects:
        props[Types.expression] = parsed_netlist_line.known_objects[Types.expression]
    build_table_expression(parsed_netlist_line, reader_state, language_device_type, props, label, value)


def handleCurrentControlledPoly(parsed_netlist_line, props, reader_state):
    if Types.poly in parsed_netlist_line.known_objects:
        poly_value = parsed_netlist_line.known_objects.get(Types.value)
        controllingVDeviceList = []
        polyValue = int(parsed_netlist_line.known_objects.get(Types.value))
        if polyValue > 0:
            parsed_netlist_line.flag_control_device = True
        for i in range(polyValue):
            controllingVDeviceList.append(parsed_netlist_line.poly_param_list[i])
        poly_coeff_list = parsed_netlist_line.poly_param_list[polyValue:]
        props[Types.polyExpression] = POLY(poly_value, controllingVDeviceList, poly_coeff_list)


def handleVoltageControlledPoly(parsed_netlist_line, props, reader_state):
    if Types.poly in parsed_netlist_line.known_objects:
        poly_value = parsed_netlist_line.known_objects.get(Types.value)
        pairedControllingNodeslist = []
        polyValue = int(parsed_netlist_line.known_objects.get(Types.value))
        for i in range(polyValue):
            node_name_1 = parsed_netlist_line.poly_param_list[i * 2]
            node_name_2 = parsed_netlist_line.poly_param_list[i * 2 + 1]
            pairedControllingNodeslist.append((build_node_by_value(parsed_netlist_line, node_name_1, reader_state),
                                               build_node_by_value(parsed_netlist_line, node_name_2, reader_state)))
        poly_coeff_list = parsed_netlist_line.poly_param_list[2 * polyValue:]
        props[Types.polyExpression] = POLY(poly_value, pairedControllingNodeslist, poly_coeff_list)


def build_control_expression(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    pass


def handle_ac_value(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    if Types.acValue in parsed_netlist_line.known_objects:
        mag = parsed_netlist_line.known_objects.get(Types.acMagValue)
        phase = parsed_netlist_line.known_objects.get(Types.acPhaseValue)
        ac = AC(mag, phase)
        props[Types.acValue] = ac


def handle_dc_value(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    if Types.dcValueValue in parsed_netlist_line.known_objects:
        dcVal = parsed_netlist_line.known_objects.get(Types.dcValueValue)
        dc = DC(dcVal)
        props[Types.dcValue] = dc


def handle_measurement_type_value(parsed_netlist_line, reader_state, language_directive_type, props, label, value):
    analysis_type = parsed_netlist_line.known_objects.get(Types.analysisTypeValue)
    if analysis_type:
        measure = MEASURE(analysis_type, parsed_netlist_line)
        measure.set_measure_type(parsed_netlist_line, language_directive_type)
        measure.set_measure_qualifier(parsed_netlist_line, language_directive_type)

        if not measure.comment:
            props[Types.measurementTypeValue] = measure
        else:
            props[Types.measurementTypeValue] = ""
            props[Types.name] = ".MEASURE " + measure.analysis_type + " " + parsed_netlist_line.known_objects["RESULT_NAME_VALUE"] + " " + measure.spice_string()
            props["COMMENT"] = props[Types.name]
            parsed_netlist_line.type = ".COMMENT"
            parsed_netlist_line.name = props[Types.name]
            build_parameters(parsed_netlist_line, props)
            comment = COMMENT(props, parsed_netlist_line.filename, parsed_netlist_line.linenum,
                              reader_state.scope_index.uid_index.uid)
            reader_state.scope_index.add(comment)

    return


def handle_transient(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    trans_type = parsed_netlist_line.known_objects.get(Types.trans_func)
    if trans_type:
        transient = TRANSIENT(trans_type)
        transient.set_transient_props(parsed_netlist_line.transient_values)
        props[Types.transient] = transient
        pwl_file = transient.pwl_file
        if pwl_file:
            reader_state.add_pwl_file(pwl_file)


def handle_sweep(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    if parsed_netlist_line.sweep_param_list:
        sweep = SWEEP()
        remaining_list = deque(parsed_netlist_line.sweep_param_list)
        if "DEC" in parsed_netlist_line.sweep_param_list:
            while len(remaining_list) > 0:
                first_item = remaining_list.popleft()
                if "DEC" == first_item:
                    first_item = remaining_list.popleft()
                sweep_var_name = first_item
                start = remaining_list.popleft()
                stop = remaining_list.popleft()
                points = remaining_list.popleft()
                dec_sweep = DEC_SWEEP(sweep_var_name, start, stop, points)
                sweep.add_sweep(dec_sweep)
        elif "OCT" in parsed_netlist_line.sweep_param_list:
            while len(remaining_list) > 0:
                first_item = remaining_list.popleft()
                if "OCT" == first_item:
                    first_item = remaining_list.popleft()
                sweep_var_name = first_item
                start = remaining_list.popleft()
                stop = remaining_list.popleft()
                points = remaining_list.popleft()
                oct_sweep = OCT_SWEEP(sweep_var_name, start, stop, points)
                sweep.add_sweep(oct_sweep)
        elif "LIST" in parsed_netlist_line.sweep_param_list:
            keyword_indices = [i for i, x in enumerate(remaining_list) if x == "LIST"]
            beginning_list_indices = [x - 1 for x in keyword_indices]
            for i, beginning in enumerate(beginning_list_indices):
                sweep_var_name = remaining_list[beginning]
                val_list = []
                if (i + 1) == len(beginning_list_indices):
                    val_list = list(itertools.islice(remaining_list, (beginning + 2), None))
                else:
                    val_list = list(itertools.islice(remaining_list, (beginning + 2), beginning_list_indices[i + 1]))
                list_sweep = LIST_SWEEP(sweep_var_name, val_list)
                sweep.add_sweep(list_sweep)
        elif "DATA" in parsed_netlist_line.sweep_param_list:
            while len(remaining_list) > 0:
                first_item = remaining_list.popleft()
                if "DATA" == first_item:
                    first_item = remaining_list.popleft()
                sweep_var_name = first_item
                data_sweep = DATA_SWEEP(sweep_var_name)
                sweep.add_sweep(data_sweep)
        else:
            while len(remaining_list) > 0:
                first_item = remaining_list.popleft()
                if "LIN" == first_item:
                    first_item = remaining_list.popleft()
                sweep_var_name = first_item
                start = remaining_list.popleft()
                stop = remaining_list.popleft()
                step = remaining_list.popleft()
                lin_sweep = LIN_SWEEP(sweep_var_name, start, stop, step)
                sweep.add_sweep(lin_sweep)
        props[Types.sweep] = sweep


def handle_params_list(parsed_netlist_line, reader_state, language_device_type, props, label, value):
    if len(parsed_netlist_line.params_dict) > 0:
        params_list_dict = {}
        for param in parsed_netlist_line.params_dict:
            params_list_dict[param] = parsed_netlist_line.params_dict[param]
        props[Types.paramsList] = params_list_dict
        parsed_netlist_line.params_dict = {}


prop_type_to_function = {  # devices
    "node": build_node,
    "name": build_name,
    "modelName": build_model_name,
    "controlType": handle_control_type,
    "controlDeviceValue": handle_control_device_value,
    "controlDeviceList": handle_control_device_list,
    "value": handle_value,  # also used for directives
    "valueExpression": build_value_expression,
    "tableExpression": build_table_expression,
    "polyExpression": build_poly_expression,
    "voltageExpression": build_voltage_expression,
    "currentExpression": build_current_expression,
    "controlExpression": build_control_expression,
    "acValue": handle_ac_value,
    "dcValue": handle_dc_value,
    "transient": handle_transient,
    "subcircuitNameValue": handle_subcircuit_name_value,
    "subcircuitParamsList": handle_subcircuit_params_list,
    "subDirNodeList": handle_sub_dir_node_list,
    "measurementTypeValue": handle_measurement_type_value,

    # directives
    "valueList": build_value_list,
    "fileNameValue": build_file_name,
    "optionPkgTypeValue": build_opt_pack_type_value,
    "scheduleValue": build_schedule_value,
    "outputVariableList": build_output_variable_list,
    "subcktName": build_subckt_name,
    "nodeList": handle_node_list,
    "interfaceNodeList": handle_interface_node_list,
    "sweep": handle_sweep,
    "paramsList": handle_params_list,
    "funcArgList": build_func_arg_list,
    "funcExpression": build_func_expression,
    "libEntry" : build_lib_entry,
    "initialConditionsList": build_initial_conditions_list
}


def string_expression_match(string1, string2):
    if string1 == string2:
        return True
    return False


def build_parameters(parsed_netlist_line, props):
    for key in parsed_netlist_line.params_dict.keys():
        props[key] = parsed_netlist_line.params_dict[key]


# def build_nodes(parsed_netlist_line, reader_state, props, language_device_types):
#     for known_object_type in parsed_netlist_line.known_objects:
#         if known_object_type in Types.node_type_list:
#             node_name = parsed_netlist_line.known_objects.get(known_object_type)
#             node = reader_state.scope_index.get_object(node_name)
#             if node is None:
#                 node = ENODE(node_name, reader_state.scope_index.uid_index.uid)
#                 reader_state.scope_index.add(node, case_insensitive=reader_state.is_case_insensitive())
#             props[known_object_type] = node
#         elif known_object_type in Types.value_type_list:
#             value = parsed_netlist_line.known_objects.get(known_object_type)
#             props[known_object_type] = value


def build_node_by_value(parsed_netlist_line, node_name, reader_state):
    node = reader_state.scope_index.get_object("__ENODE__" + node_name)
    if node is None:
        node = ENODE(node_name, reader_state.scope_index.uid_index.uid)
        reader_state.scope_index.add(node, case_insensitive=reader_state.is_case_insensitive())
    return node


def handle_device_model(device, parsed_netlist_line, reader_state):
    model_name = parsed_netlist_line.known_objects.get(Types.modelName)

    if parsed_netlist_line.known_objects.get(Types.vbicModel):
        model_name = parsed_netlist_line.known_objects.get(Types.vbicModel) + parsed_netlist_line.known_objects.get(
            Types.vbicModelName)

    if model_name is None:
        return

    if reader_state.is_case_insensitive():
        model_name = model_name.upper()

    model = reader_state.scope_index.get_object("__MODELDEF__" + model_name)
    # check to see if it is binned model
    if model is None:
        model = reader_state.scope_index.get_object("__MODELDEF__" + model_name + ".1")
    # finally, check to see if model is defined in another scope
    if model is None and parsed_netlist_line.model_def_scope:
        model = parsed_netlist_line.model_def_scope.get_object("__MODELDEF__" + model_name)

    if isinstance(model, MASTER_MODEL):
        # model defined already
        device.model = model
    else:
        existing_lazy = reader_state.scope_index.get_object("__LAZYSTATEMENT__" + model_name)
        if not existing_lazy:
            # lazy object is added to device below, model not yet defined
            model = reader_state.scope_index.add_lazy_statement(model_name, reader_state.scope_index.uid_index.uid)
            device.set_lazy_statement(model, [MASTER_MODEL])
        else:
            # handle existing lazy statement?
            device.set_lazy_statement(existing_lazy, [MASTER_MODEL])


def handle_m_param(device, language_device_type, parsed_netlist_line):
    if not parsed_netlist_line.m_param:
        return

    if not language_device_type.m_flag:
        return

    param_to_change = language_device_type.m_flag.label_key

    if param_to_change not in device.params.keys():
        return

    language_param_with_m = language_device_type.m_flag
    param_key = language_param_with_m.label_key
    m_action = language_param_with_m.m_flag  # div or mult

    old_param_value = device.params[param_key]
    m_param_value = device.params['M']

    operand = '*'
    if m_action == "div":
        operand = '/'

    new_param_value = '{' + old_param_value + operand + m_param_value + '}'

    device.params[param_key] = new_param_value
    del device.params['M']


def handle_ambiguous_references(device, parsed_netlist_line, reader_state, device_type):
    ambiguity_token_list = device_type.ambiguity_token_list
    ambiguity_length = len(ambiguity_token_list)

    # ambiguity length matches lazy statement length, so match them together in order
    if ambiguity_length == len(parsed_netlist_line.lazy_statements):
        for i in range(ambiguity_length):
            ambiguity_token_label = ambiguity_token_list[i].value
            lazy_statement_name = list(parsed_netlist_line.lazy_statements.items())[i][0]
            if ambiguity_token_label == "modelName":
                parsed_netlist_line.add_known_object(lazy_statement_name, Types.modelName)
            else:
                device.add_param(ambiguity_token_label, lazy_statement_name)
        # TODO: delete lazy statements
        for key, value in list(parsed_netlist_line.lazy_statements.items()):
            del parsed_netlist_line.lazy_statements[key]
    # ambiguity length is more than lazy statements, so assign the lazy statements to the device
    elif ambiguity_length > len(parsed_netlist_line.lazy_statements):

        # gets all of the possible types from the XML
        xml_possible_types_list = []
        for ambiguity_token in ambiguity_token_list:
            label = ambiguity_token.value
            if label == "model":
                label = Types.modelName
            xml_possible_types_list.append(label)

        # iterate through the lazy statement dict
        for lazy_statement in parsed_netlist_line.lazy_statements:
            ambig_obj = reader_state.scope_index.get_object(lazy_statement)
            if isinstance(ambig_obj, MASTER_MODEL):
                # it's a model, so set the model - no other lazy statements to worry about
                device.model = ambig_obj
            else:
                # need to set lazy statement to device, with all possible types from XML list
                possible_types_list = []
                possible_string_key = None
                for ambiguity_token in ambiguity_token_list:
                    label = ambiguity_token.value
                    if label == "modelName":
                        label = Types.modelName
                    else:
                        possible_types_list.append(label)

                for possible_type in parsed_netlist_line.lazy_statements[lazy_statement]:
                    if possible_type == Types.value:
                        pass
                    else:
                        possible_types_list.append(generic_map_dict[possible_type])

                if ambig_obj is not None:
                    device.set_lazy_statement(ambig_obj, possible_types_list)
                else:
                    ambig_obj = reader_state.scope_index.add_lazy_statement(lazy_statement,
                                                                            reader_state.scope_index.uid_index.uid)
                    device.set_lazy_statement(ambig_obj, possible_types_list)


def is_supported_device(parsed_netlist_line):
    # print parsed_netlist_line.type
    if parsed_netlist_line:
        return parsed_netlist_line.type.upper() in supported_devices


def is_supported_directive(parsed_netlist_line):
    if parsed_netlist_line:
        return parsed_netlist_line.type in supported_directives


def is_unknown_device(parsed_netlist_line):
    """If pnl has name and no type, it's unknown"""
    if parsed_netlist_line:
        return not parsed_netlist_line.type and parsed_netlist_line.name


def build_value_prop(parsed_netlist_line, value_type):
    return parsed_netlist_line.known_objects.get(value_type)


# used in directives - probably remove soon
def handleOutputVariables(parsed_netlist_line, props, reader_state):
    return parsed_netlist_line.output_variable_values


def convert_list_to_node_list(parsed_netlist_line, reader_state):
    node_list = []
    for node_string in parsed_netlist_line.value_list:
        node_list.append(build_node_by_value(parsed_netlist_line, node_string, reader_state))
    return node_list


def build_device(parsed_netlist_line, reader_state, language_definition):
    props = {}
    params = {}
    device_type = parsed_netlist_line.type

    # NEED to handle different levels of devices (currently just taking default)
    # Update 2019-07-09: If the pnl is an instantiation of a model (checked by seeing if "MODEL_NAME" in known_objects, 
    #                    see "else" block), it will be added to the unknown_pnl list first so that the correct instance
    #                    can be found. It will then be resolved later in the GenericReader (see line 185 of GenericReader).
    #                    Not too sure if the first branch is needed, but will leave in for now
    if parsed_netlist_line.known_objects.get(Types.vbicModel):
        language_device_type = language_definition.get_device_by_name_level(device_type, "10")
    elif parsed_netlist_line.params_dict.get("LEVEL"):
        if parsed_netlist_line.params_dict.get("VERSION"):
            language_device_type = language_definition.get_device_by_name_level(device_type, 
                                                                            parsed_netlist_line.params_dict["LEVEL"], parsed_netlist_line.params_dict["VERSION"])
            del parsed_netlist_line.params_dict["VERSION"]
        else:
            language_device_type = language_definition.get_device_by_name_level(device_type,
                                                                            parsed_netlist_line.params_dict["LEVEL"])
        del parsed_netlist_line.params_dict["LEVEL"]
    else:
        if "MODEL_NAME" in parsed_netlist_line.known_objects and parsed_netlist_line.type != "X" and not parsed_netlist_line.flag_unresolved_device:
            parsed_netlist_line.flag_unresolved_device = True
            reader_state.add_unknown_pnl(parsed_netlist_line)
            return None
        else:
            language_device_type = language_definition.get_default_definition(parsed_netlist_line.local_type)
            if parsed_netlist_line.flag_unresolved_device:
                model_name = parsed_netlist_line.known_objects["MODEL_NAME"]

    if language_device_type:

        if len(parsed_netlist_line.unknown_nodes) > 0:

            node_types = language_device_type.node_types
            for i in range(len(parsed_netlist_line.unknown_nodes)):
                if len(node_types) <= i:
                    logging.warning("Line(s):" + str(parsed_netlist_line.linenum) + ". Too many nodes defined for device type="+language_device_type.name+" level="+language_device_type.level+".")
                    continue

                try:
                    node_type = eval('Types.' + node_types[i].label.strip())
                    # print node_type
                except:
                    logging.warning("Line(s):" + str(
                        parsed_netlist_line.linenum) + ". No node type defined internally for type found in XML: " +
                                    node_types[i].label.strip())
                    continue
                parsed_netlist_line.add_known_object(parsed_netlist_line.unknown_nodes[i], node_type)

        for key, value in language_device_type.props.items():
            prop_type_to_function[value.prop_type](parsed_netlist_line, reader_state, language_device_type, props,
                                                   value.label, value.value)

        for key, value in language_device_type.params.items():
            handle_value(parsed_netlist_line, reader_state, language_device_type, params, value.label, value.value)

        for unsupported_param in parsed_netlist_line.params_dict:
            if parsed_netlist_line.type != "X":
                logging.warning("In file:\"" + str(os.path.basename(parsed_netlist_line.filename))
                                + "\" at Line(s):" + str(
                    parsed_netlist_line.linenum) + ". Param removed. No param defined internally in XML: " + unsupported_param)

        # inline comment
        if parsed_netlist_line.params_dict.get(Types.comment):
            props[Types.comment] = parsed_netlist_line.params_dict.get(Types.comment)

        # check if ground node synonyms are present in nodes of subckt instantiation 
        # if so, put into parsed netlist line object preprocess directive
        if parsed_netlist_line.type == "X":
            for node_name in parsed_netlist_line.subckt_device_param_list[:-1]:
                if node_name.lower() in ["gnd", "gnd!", "ground"]:
                    # check to make sure ground node synonym is not one of the subcircuit's interface
                    # nodes. if it is, do not add the preprocess directive
                    is_interface_node = False
                    if reader_state.scope_index.subckt_command:
                        for interface_node in reader_state.scope_index.subckt_command.props["INTERFACE_NODE_LIST"]:
                            if node_name == interface_node.name:
                                is_interface_node = True
                                break

                    if not "REPLACEGROUND TRUE" in parsed_netlist_line.preprocess_keyword_value and not is_interface_node:
                        parsed_netlist_line.add_preprocess_keyword_value("REPLACEGROUND TRUE")

        if parsed_netlist_line.flag_unresolved_device:
            props['MODEL_NAME'] = model_name

        device = Device(props, params, parsed_netlist_line.filename, parsed_netlist_line.linenum,
                        reader_state.scope_index.uid_index.uid)

        if parsed_netlist_line.flag_control_device:
            device.resolve_control_devices = True

        device.device_type = language_device_type.device_type
        device.device_level = language_device_type.device_level
        device.device_level_key = language_device_type.device_level_key
        device.device_version = language_device_type.device_version
        device.device_version_key = language_device_type.device_version_key

        handle_ambiguous_references(device, parsed_netlist_line, reader_state, language_device_type)
        handle_device_model(device, parsed_netlist_line, reader_state)
        handle_m_param(device, language_device_type, parsed_netlist_line)
        device.inline_comment = parsed_netlist_line.comment

        reader_state.scope_index.add_device(device, reader_state.is_case_insensitive())
        return device
    else:
        logging.warning("Line(s):" + str(
            parsed_netlist_line.linenum) + ". Device Type not found in XML: " + parsed_netlist_line.local_type)

    return None


def build_model(parsed_netlist_line, reader_state, language_definition):
    props = {}
    params = {}

    model_device_type = model_map_dict.get(parsed_netlist_line.known_objects.get(Types.modelType).upper())

    if not model_device_type:
        model_device_type = parsed_netlist_line.known_objects.get(Types.modelType)

    level = "1"
    version = ""
    if parsed_netlist_line.params_dict.get("LEVEL"):
        level = parsed_netlist_line.params_dict["LEVEL"]
        del parsed_netlist_line.params_dict["LEVEL"]

    if parsed_netlist_line.params_dict.get("VERSION"):
        version = parsed_netlist_line.params_dict["VERSION"]
        del parsed_netlist_line.params_dict["VERSION"]

    language_device_types = language_definition.get_devices_by_local_name(model_device_type)
    language_device_type = None
    if len(language_device_types) == 1:
        language_device_type = language_device_types[0]
    else:
        language_device_type = language_definition.get_device_by_name_level(model_device_type, level, version)

        if language_device_type is None and version:
            language_device_type = language_definition.get_device_by_name_level(model_device_type, level, "")

            if language_device_type:
                logging.warning("Line(s):" + str(
                    parsed_netlist_line.linenum) + ". Model version not found in XML: " + parsed_netlist_line.known_objects.get(
                    Types.modelType) + " Level: " + level + " Version: " + version + ". Using default version.")
                version = ""
                

    if language_device_type:
        lang_device_model = language_device_type.model
        if lang_device_model:
            for key, value in lang_device_model.props.items():
                prop_type_to_function[value.prop_type](parsed_netlist_line, reader_state, lang_device_model, props,
                                                       value.label, value.value)

            for key, value in lang_device_model.params.items():
                handle_value(parsed_netlist_line, reader_state, lang_device_model, params, value.label, value.value)

            for unsupported_param in parsed_netlist_line.params_dict:
                logging.warning("In file:\"" + str(os.path.basename(parsed_netlist_line.filename))
                                + "\" at Line(s):" + str(parsed_netlist_line.linenum) + ". Param removed. No param defined internally in XML: " + unsupported_param)

            # inline comment
            if parsed_netlist_line.params_dict.get(Types.comment):
                props[Types.comment] = parsed_netlist_line.params_dict.get(Types.comment)

            model = ModelDef(props, params, parsed_netlist_line.filename, parsed_netlist_line.linenum,
                             reader_state.scope_index.uid_index.uid)
            model.device_type = language_device_type.device_type
            model.device_local_type = language_device_type.device_local_type
            model.device_level = language_device_type.device_level
            model.device_level_key = language_device_type.device_level_key
            model.device_version = language_device_type.device_version
            model.device_version_key = language_device_type.device_version_key
            model.inline_comment = parsed_netlist_line.comment
            reader_state.scope_index.add_model(model, reader_state.is_case_insensitive())
            return model
        else:
            logging.warning("Line(s):" + str(
                parsed_netlist_line.linenum) + ". Model type not found in XML: " + parsed_netlist_line.known_objects.get(
                Types.modelType))
            return None
    else:
        logging.warning("Line(s):" + str(
            parsed_netlist_line.linenum) + ". Model type not found in XML: " + parsed_netlist_line.known_objects.get(
            Types.modelType) + " Level: " + level + " Version: " + version)


def build_comment(parsed_netlist_line, reader_state):
    props = {}
    props[Types.name] = parsed_netlist_line.name
    build_parameters(parsed_netlist_line, props)
    comment = COMMENT(props, parsed_netlist_line.filename, parsed_netlist_line.linenum,
                      reader_state.scope_index.uid_index.uid)
    reader_state.scope_index.add(comment)


def build_title(parsed_netlist_line, reader_state):
    props = {Types.name: parsed_netlist_line.name}
    build_parameters(parsed_netlist_line, props)
    title = TITLE(props, parsed_netlist_line.filename, parsed_netlist_line.linenum,
                  reader_state.scope_index.uid_index.uid)
    reader_state.scope_index.add(title)


def build_data(parsed_netlist_line, reader_state):
    props = {Types.name: parsed_netlist_line.name}
    props[Types.valueList] = parsed_netlist_line.value_list
    data = DATA(props, parsed_netlist_line.filename, parsed_netlist_line.linenum,
                  reader_state.scope_index.uid_index.uid)
    reader_state.scope_index.add(data)


def build_directive(parsed_netlist_line, reader_state, language_definition, lib_sect_list):
    props = {}
    params = {}
    directive_type = parsed_netlist_line.type
    language_directive_type = language_definition.get_directive_by_name(directive_type)

    if parsed_netlist_line.flag_unresolved_device:
        reader_state.add_unknown_pnl(parsed_netlist_line)
        return None

    if language_directive_type:

        for key, value in language_directive_type.props.items():
            prop_type_to_function[value.prop_type](parsed_netlist_line, reader_state, language_directive_type, props,
                                                   value.label, value.value)
        if directive_type == ".TRAN" and not props.get(Types.printStepValue):
            props[Types.printStepValue] = "0"

        # Execptions for Spectre
        # For .AC directives, Spectre does not require sweep types to be declared. Therefore,
        # a default type needs to be included in translation. This replicates the Spectre
        # default .AC sweep type as closely as possible
        if directive_type == ".AC" and language_definition.language == "spectre" and props.get(Types.sweepTypeValue) == None:
            props[Types.sweepTypeValue] = "DEC"
            props[Types.pointsValue] = "50"

        # For .GLOBAL directives, the first node listed is considered a ground node. For now,
        # if that is the only node listed (which is indicated by the pnl object having no props), 
        # skip creating a data model object for it.
        elif directive_type == ".GLOBAL" and language_definition.language == "spectre" and props.get(Types.generalNodeName) == None:
            return None

        for key, value in language_directive_type.params.items():
            handle_value(parsed_netlist_line, reader_state, language_directive_type, params, value.label, value.value)

        if directive_type == ".PRINT" and not props.get(Types.analysisTypeValue):
            props[Types.analysisTypeValue] = "TRAN"

        for unsupported_param in parsed_netlist_line.params_dict:
            if parsed_netlist_line.type != ".SUBCKT":
                logging.warning("In file:\"" + str(os.path.basename(parsed_netlist_line.filename))
                                + "\" at Line(s):" + str(
                    parsed_netlist_line.linenum) + ". Param removed. No param defined internally in XML: " + unsupported_param)

        # props[Types.name] = directive_type

        # for case .MEASURE is not valid and commented out
        if Types.measurementTypeValue in props:
            if not props[Types.measurementTypeValue]:
                return None

        directive = Command(props, params, parsed_netlist_line.filename, parsed_netlist_line.linenum,
                            reader_state.scope_index.uid_index.uid)
        directive.command_type = directive_type
        directive.inline_comment = parsed_netlist_line.comment
        reader_state.scope_index.add(directive, reader_state.is_case_insensitive())

        if directive_type == ".SUBCKT":
            reader_state.scope_index = reader_state.scope_index.push_scope(subckt_command=directive)
        elif directive_type == ".ENDS":
            reader_state.scope_index = reader_state.scope_index.pop_scope()

        # If library section is the one of the called sections, stay at current scope.
        # If library section is different section than the one desired, put in child scope to avoid
        # name conflicts.
        if directive_type == ".LIB":

            if "LIB_ENTRY" in directive.props:
                curr_lib_name = directive.props["LIB_ENTRY"]

                if language_definition.is_case_insensitive:
                    curr_lib_name = curr_lib_name.upper()
                    if lib_sect_list:
                        lib_sect_list = [sect.upper() for sect in lib_sect_list]

            if "FILENAME_VALUE" in directive.props:
                pass
            elif curr_lib_name in lib_sect_list:
                pass
            else:
                reader_state.scope_index = reader_state.scope_index.push_scope(lib_command=directive)
        elif directive_type == ".ENDL":
            reader_state.scope_index = reader_state.scope_index.pop_scope()

        return directive
    else:
        logging.warning(
            "Line(s):" + str(parsed_netlist_line.linenum) + ". Directive type not found in XML: " + directive_type)

    return None
