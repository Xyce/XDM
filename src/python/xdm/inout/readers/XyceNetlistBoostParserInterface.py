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
import sys
import os

import SpiritCommon

import xdm.Types as Types

from xdm.inout.readers import BoostParserInterface
from xdm.inout.readers.ParsedNetlistLine import ParsedNetlistLine


class XyceNetlistBoostParserInterface(object):
    """
    Allows for Xyce to be read in using the Boost Parser.  Iterates over
    statements within the Xyce netlist file.
    """

    def __init__(self, filename, language_definition, top_level_file=True):
        self.internal_parser = SpiritCommon.XyceNetlistBoostParser()
        self.goodfile = self.internal_parser.open(filename, top_level_file)
        self.line_iter = iter(self.internal_parser)
        self._filename = filename
        self._language_definition = language_definition
        self._top_level_file = top_level_file

        if not self.goodfile:
            logging.error("File: " + filename + " was not found. Please locate this file and try again.\n\n\n")
            sys.exit(1)

        # a list of parsed netlist line objects created during
        # conversion to adm.
        self._synthesized_pnls = []

    def __del__(self):
        self.internal_parser.close()

    def __iter__(self):
        return self

    def __next__(self, silent=False):

        boost_parsed_line = next(self.line_iter)

        pnl = ParsedNetlistLine(boost_parsed_line.filename, boost_parsed_line.linenums)

        parsed_object_iter = iter(boost_parsed_line.parsed_objects)

        for parsedObject in parsed_object_iter:
            self.convert_next_token(parsedObject, parsed_object_iter, pnl, self._synthesized_pnls)

        return pnl

    @staticmethod
    def convert_next_token(parsed_object, parsed_object_iter, pnl, synthesized_pnls):
        """
        Takes individual parsed objects from the parsed line object

        Populate ParsedNetlistLine class with all information necessary to create a Statement

        Many hacks contained here
        """

        if parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME or parsed_object.types[0] == SpiritCommon.data_model_type.DEVICE_TYPE:

            pnl.local_type = parsed_object.value.upper()
            if parsed_object.value.upper() == ".TR":
                pnl.type = ".TRAN"
            elif parsed_object.value.upper() == ".INITCOND":
                pnl.type = ".IC"
            else:
                pnl.type = parsed_object.value.upper()

        elif parsed_object.types[0] == SpiritCommon.data_model_type.DEVICE_NAME or (
                parsed_object.types[0] == SpiritCommon.data_model_type.MODEL_NAME and pnl.type == ".MODEL"):
            pnl.name = parsed_object.value

        elif parsed_object.types[0] == SpiritCommon.data_model_type.PARAM_NAME:

            param_value_parsed_object = next(parsed_object_iter)

            if param_value_parsed_object.types[0] != SpiritCommon.data_model_type.PARAM_VALUE:
                logging.error(
                    "Line(s):" + str(pnl.linenum) + ". Parser passed wrong token.  Expected PARAM_VALUE.  Got " + str(
                        param_value_parsed_object.types[0]))
                raise Exception("Next Token is not a PARAM_VALUE.  Something went wrong!")

            pnl.add_param_value_pair(parsed_object.value.upper(), param_value_parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.STANDALONE_PARAM:

            pnl.add_param_value_pair(parsed_object.value.upper(), "1")

        elif parsed_object.types[0] == SpiritCommon.data_model_type.MEASURE_PARAM_NAME:

            param_value_parsed_object = next(parsed_object_iter)

            if param_value_parsed_object.types[0] != SpiritCommon.data_model_type.MEASURE_PARAM_VALUE:
                logging.error(
                    "Line(s):" + str(pnl.linenum) + ". Parser passed wrong token.  Expected MEASURE_PARAM_VALUE.  Got " + str(
                        param_value_parsed_object.types[0]))
                raise Exception("Next Token is not a MEASURE_PARAM_VALUE.  Something went wrong!")

            pnl.add_meas_param_value_pair(list(pnl.meas_dict.items())[-1][0], parsed_object.value.upper(), param_value_parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.VARIABLE_EXPR_OR_VALUE:

            sentinel = object()
            param_value_parsed_object = next(parsed_object_iter, sentinel)
            hasNext = param_value_parsed_object is not sentinel

            if not hasNext:
                pnl.add_meas_param_value_pair(list(pnl.meas_dict.items())[-1][0], parsed_object.value.upper(), "")

            else:
                if param_value_parsed_object.types[0] == SpiritCommon.data_model_type.VARIABLE_EXPR_OR_VALUE:
                    pnl.add_meas_param_value_pair(list(pnl.meas_dict.items())[-1][0], parsed_object.value.upper(), param_value_parsed_object.value)

                elif param_value_parsed_object.types[0] == SpiritCommon.data_model_type.MEASURE_PARAM_NAME:
                    pnl.add_meas_param_value_pair(list(pnl.meas_dict.items())[-1][0], parsed_object.value.upper(), "")

                    param_value_parsed_object_2 = next(parsed_object_iter)

                    if param_value_parsed_object_2.types[0] != SpiritCommon.data_model_type.MEASURE_PARAM_VALUE:
                        logging.error(
                            "Line(s):" + str(pnl.linenum) + ". Parser passed wrong token.  Expected MEASURE_PARAM_VALUE.  Got " + str(
                                param_value_parsed_object_2.types[0]))
                        raise Exception("Next Token is not a MEASURE_PARAM_VALUE.  Something went wrong!")

                    pnl.add_meas_param_value_pair(list(pnl.meas_dict.items())[-1][0], param_value_parsed_object.value.upper(), param_value_parsed_object_2.value)

                else:
                    logging.error(
                        "Line(s):" + str(pnl.linenum) + ". Parser passed wrong token.  Expected VARIABLE_EXPR_OR_VALUE or MEASURE_PARAM_VALUE.  Got " + str(
                            param_value_parsed_object.types[0]))
                    raise Exception("Next Token is not a VARIABLE_EXPR_OR_VALUE or MEASURE_PARAM_VALUE.  Something went wrong!")

        elif parsed_object.types[0] == SpiritCommon.data_model_type.PARAM_VALUE and pnl.params_dict:
            last_key = list(pnl.params_dict.keys())[-1]
            prev_param_value = pnl.params_dict[last_key]
            pnl.params_dict[last_key] = prev_param_value+" "+parsed_object.value

        elif parsed_object.types[0] == SpiritCommon.data_model_type.CONTROL_DEVICE:

            control_dev_name_obj = next(parsed_object_iter)

            if control_dev_name_obj.types[0] != SpiritCommon.data_model_type.CONTROL_DEVICE_NAME:
                logging.error("Line(s):" + str(
                    pnl.linenum) + ". Parser passed wrong token.  Expected CONTROL_DEVICE_NAME.  Got " + str(
                    control_dev_name_obj.types[0]))
                raise Exception("Next Token is not a CONTROL_DEVICE_NAME.  Something went wrong!")

            pnl.add_control_param_value(parsed_object.value + control_dev_name_obj.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.SWEEP_PARAM_VALUE:

            pnl.add_sweep_param_value(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.SCHEDULE_PARAM_VALUE:

            pnl.add_schedule_param_value(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.LIST_PARAM_VALUE:

            pnl.add_value_to_value_list(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.TABLE_PARAM_VALUE:

            pnl.add_table_param_value(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.POLY_PARAM_VALUE:

            pnl.add_poly_param_value(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.DATA_PARAM_NAME:

            pnl.add_value_to_value_list(parsed_object.value)

            pnl_synth = ParsedNetlistLine(pnl.filename, [pnl.linenum[0]-1])
            pnl_synth.type = ".GLOBAL_PARAM"
            pnl_synth.local_type = ".GLOBAL_PARAM"

            pnl_synth.add_param_value_pair(parsed_object.value.upper(), "0")
            synthesized_pnls.append(pnl_synth)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.DATA_PARAM_VALUE:

            if not pnl.type:
                pnl.type = "DATA"
                pnl.name = parsed_object.value
            else:
                pnl.name += " "+parsed_object.value

            pnl.add_value_to_value_list(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.MEASURE_TYPE or parsed_object.types[0] == SpiritCommon.data_model_type.MEASURE_QUALIFIER:

            pnl.add_meas_analysis_condition(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.CONTROL_PARAM_VALUE:

            pnl.add_control_param_value(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.SUBCKT_DIRECTIVE_PARAM_VALUE:

            pnl.add_subckt_directive_param_value(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.SUBCKT_DEVICE_PARAM_VALUE:

            pnl.add_subckt_device_param_value(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.TRANS_REF_NAME:
            pnl.add_transient_value(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.OUTPUT_VARIABLE:
            pnl.add_output_variable_value(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.FUNC_ARG_VALUE:
            pnl.add_func_arg_value(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.INLINE_COMMENT:
            pnl.add_inline_comment(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.TITLE:
            pnl.type = "TITLE"
            pnl.name = parsed_object.value
            pnl.add_comment(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.COMMENT:
            pnl.type = "COMMENT"
            try:
                pnl.name = parsed_object.value[1:]
                pnl.add_comment(parsed_object.value[1:])
            except UnicodeDecodeError as e:
                logging.warning("Non-ASCII character detected in the comment within file '" + str(os.path.basename(pnl.filename)) + "' " + "at line number(s) " + str(pnl.linenum) )
                warning_msg = " Non-ascii character encountered on line " + str(pnl.linenum) +". Omitting... "
                pnl.name = warning_msg
                pnl.add_comment(warning_msg)

        elif parsed_object.types[0] in [SpiritCommon.data_model_type.VOLTAGE, parsed_object.types[0] == SpiritCommon.data_model_type.CURRENT] and pnl.type in [".IC", ".DCVOLT", ".NODESET"]:
            initial_condition_dict = {}
            initial_condition_dict[Types.voltageOrCurrent] = parsed_object.value
            pnl.initial_conditions_list.append(initial_condition_dict)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.GENERALNODE and pnl.type in [".IC", ".DCVOLT", ".NODESET"]:
            output_node = parsed_object.value.replace(".", ":")

            if not pnl.initial_conditions_list:
                initial_condition_dict = {}
                initial_condition_dict[Types.voltageOrCurrent] = "V"
                initial_condition_dict[Types.generalNodeName] = output_node
                pnl.initial_conditions_list.append(initial_condition_dict)
                
            elif Types.generalNodeName in pnl.initial_conditions_list[-1]:
                initial_condition_dict = {}
                initial_condition_dict[Types.voltageOrCurrent] = "V"
                initial_condition_dict[Types.generalNodeName] = output_node
                pnl.initial_conditions_list.append(initial_condition_dict)

            else:
                pnl.initial_conditions_list[-1][Types.generalNodeName] = output_node

        elif parsed_object.types[0] == SpiritCommon.data_model_type.GENERAL_VALUE and pnl.type in [".IC", ".DCVOLT", ".NODESET"]:
            pnl.initial_conditions_list[-1][Types.generalValue] = parsed_object.value

        elif len(parsed_object.types) == 1:
            pnl.add_known_object(parsed_object.value, BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]])

            if parsed_object.types[0] == SpiritCommon.data_model_type.TEMPERATURENODE:
                pnl.add_param_value_pair("TNODEOUT", "1")

        else:
            lst = []
            for typ in parsed_object.types:
                lst.append(BoostParserInterface.boost_xdm_map_dict[typ])
            pnl.add_lazy_statement(parsed_object.value, lst)

        return
