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
import sys

import SpiritCommon
import SpiritExprCommon


from xdm import Types
from xdm.expr import expr_utils
from xdm.inout.readers import BoostParserInterface
from xdm.inout.readers.ParsedNetlistLine import ParsedNetlistLine
from xdm.inout.readers.XDMFactory import supported_devices
from xdm.inout.readers.XyceNetlistBoostParserInterface import XyceNetlistBoostParserInterface


# maps hspice model types into their ADM (xyce style) model types
hspice_to_adm_model_type_map = {"RES": "R",
                                "IND": "L",
                                "CORE": "CORE",
                                "D": "D",
                                "CAP": "C",
                                "PNP": "PNP",
                                "NPN": "NPN",
                                "LPNP": "LPNP", # assuming it is the same - q device
                                "NIGBT": "NMF", # is this right?
                                "NMOS": "NMOS",
                                "PMOS": "PMOS",
                                "DOUTPUT": "LTRA", # is this right?
                                "VSWITCH": "VSWITCH",
                                "ISWITCH": "ISWITCH",
                                "UADC": "DIG", # U devices?
                                "UDAC": "DIG",
                                "UDLY": "DIG",
                                "UEFF": "DIG",
                                "UGATE": "DIG",
                                "UGFF": "DIG",
                                "UIO": "DIG",
                                "UTGATE": "DIG",
                                "NJF": "NJF",
                                "PJF": "PJF",
                                "GASFET": "B", # does not exist in reference manual
                                "DINPUT": "N", # N device does not exist in Xyce
                                "TRN": "LTRA" # is this right? O device in Xyce is T device in HSPICE?
                                }

default_values = {
    "ITL1": "200",
    "ITL4": "20"
}


class HSPICENetlistBoostParserInterface:
    """
    Allows for HSPICE to be read in using the Boost Parser.  Iterates over
    statements within the HSPICE netlist fiAle.
    """
    def __init__(self, filename, language_definition, top_level_file = True):
        self.internal_parser = SpiritCommon.HSPICENetlistBoostParser()
        self.goodfile = self.internal_parser.open(filename, top_level_file)
        self.line_iter = iter(self.internal_parser)
        self._filename = filename
        self._language_definition = language_definition
        self._top_level_file = top_level_file
        self._tnom_defined = False
        self._temp_defined = False
        self._tnom_value = "25"
        self._data_driven = False
        self._np = -1

        # Comment out IF statements and any conditional block for it for now
        self._if_statement = False
        self._comment_end_of_if_statement = False
        self._nested_if_statement_count = 0

        self._pkg_dict = {}

        for package_type, prop_type_list in self._language_definition.get_directive_by_name(".OPTIONS").nested_prop_dict.items():
            for prop_type in prop_type_list:
                if prop_type.label.upper() in self._pkg_dict.keys():
                    self._pkg_dict[prop_type.label.upper()].append(package_type)
                else:
                    self._pkg_dict[prop_type.label.upper()] = [package_type]

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
        """
        Iterates over parsed line, which is a collection of parsed objects
        """

        # if there are synthesized objects, return these before continuing with file parse
        if len(self._synthesized_pnls) > 0:
            return self._synthesized_pnls.pop()

        boost_parsed_line = next(self.line_iter)

        pnl = ParsedNetlistLine(boost_parsed_line.filename, boost_parsed_line.linenums)

        parsed_object_iter = iter(boost_parsed_line.parsed_objects)

        for parsedObject in parsed_object_iter:
            self.convert_next_token(parsedObject, parsed_object_iter, pnl, self._synthesized_pnls, self._pkg_dict)

        # Hack for if statements - comment out line
        if self._if_statement:
            pnl.type = "COMMENT"
            pnl.add_comment(boost_parsed_line.sourceline)
            logging.warning("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(pnl.linenum) + ". If statement cannot be translated. Continuing.")

        if self._comment_end_of_if_statement:
            pnl.type = "COMMENT"
            pnl.add_comment(boost_parsed_line.sourceline)
            self._comment_end_of_if_statement = False
            logging.warning("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(pnl.linenum) + ". If statement cannot be translated. Continuing.")

        if not silent:
            if boost_parsed_line.error_type == "critical":
                pnl.error_type = boost_parsed_line.error_type
                pnl.error_message = boost_parsed_line.error_message
                logging.critical("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(pnl.linenum) + ". " + boost_parsed_line.error_message)
            elif boost_parsed_line.error_type == "error":
                pnl.error_type = boost_parsed_line.error_type
                pnl.error_message = boost_parsed_line.error_message
                logging.error("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(pnl.linenum) + ". " + boost_parsed_line.error_message)
            elif boost_parsed_line.error_type == "warn":
                pnl.error_type = boost_parsed_line.error_type
                pnl.error_message = boost_parsed_line.error_message
                logging.warning("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(pnl.linenum) + ". " + boost_parsed_line.error_message)
            elif boost_parsed_line.error_type == "info":
                pnl.error_type = boost_parsed_line.error_type
                pnl.error_message = boost_parsed_line.error_message
                logging.info("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(pnl.linenum) + ". " + boost_parsed_line.error_message)
            else:
                pnl.error_type = " "

        return pnl

    def convert_next_token(self, parsed_object, parsed_object_iter, pnl, synthesized_pnls, pkg_dict):
        """
        Takes individual parsed objects from the parsed line object

        Populate ParsedNetlistLine class with all information necessary to create a Statement

        Many hacks contained here
        """


        if (parsed_object.types[0] == SpiritCommon.data_model_type.PARAM_NAME or parsed_object.types[0] == SpiritCommon.data_model_type.DEFAULT_PARAM_NAME) and (pnl.type == ".OPTION" or pnl.local_type == ".OPTIONS"):
            pnl.type = ".OPTIONS"
            pnl.local_type = ".OPTIONS"

            # GITLAB ISSUE #252: all options now will only appear once, at top netlist
            if not self._top_level_file:
                pnl.flag_top_pnl = True

            # find the adm option name
            orig_param_name = parsed_object.value.upper()
            param_name = orig_param_name

            # find all adm packages that use this parameter
            pkgs = pkg_dict.get(param_name.upper())

            # TODO: Hack Bugzilla 2020, ITL1 => NONLIN MAXSTEP (default 200)
            # TODO: Hack Bugzilla 2020, ITL4 => NONLIN-TRAN MAXSTEP (default 20)

            # TODO: Hack Bugzilla 2020, VNTOL => ABSTOL

            param_name, pkgs = self.hack_packages_bugzilla_2020(param_name.upper(), pkgs)

            if pkgs and param_name.upper() in ["TNOM", "SCALE"]:
                if param_name.upper() == "TNOM":
                    self._tnom_defined = True

                pnl.name = ""
                if parsed_object.types[0] == SpiritCommon.data_model_type.PARAM_NAME:
                    param_value_parsed_object = next(parsed_object_iter)
                    param_value = param_value_parsed_object.value
                else:
                    param_value = self.get_default(orig_param_name)

                pnl.add_known_object(pkgs[0], Types.optionPkgTypeValue)

                # converting .OPTIONS METHOD=DEFAULT to .OPTIONS TIMEINT METHOD=TRAP
                if param_name.upper() == "METHOD" and param_value.upper() == "DEFAULT":
                    param_value = "TRAP"

                pnl.add_param_value_pair(param_name.upper(), param_value)
                if "COMMENT" in pnl.params_dict:
                    pnl.add_inline_comment(pnl.params_dict["COMMENT"])
                    pnl.params_dict.pop("COMMENT")

                for otherPkg in pkgs[1:]:
                    pnl_synth = ParsedNetlistLine(pnl.filename, pnl.linenum)  # what to do with line numbers?
                    pnl_synth.type = ".OPTIONS"
                    pnl_synth.add_known_object(otherPkg, Types.optionPkgTypeValue)
                    pnl_synth.add_param_value_pair(param_name.upper(), param_value)
                    synthesized_pnls.append(pnl_synth)

            else:
                logging.warning("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(pnl.linenum) + ". Could not accept .OPTIONS \"" + orig_param_name.upper() + "\". Retained (as a comment). Continuing.")
                param_value_parsed_object = next(parsed_object_iter)
                if pnl.known_objects:
                    pnl.type = ".OPTIONS"
                    pnl.name = ""
                    if pnl.comment:
                        pnl.add_inline_comment(pnl.comment + " " + ".OPTIONS " + orig_param_name + " " + param_value_parsed_object.value)
                    else:
                        pnl.add_inline_comment(".OPTIONS " + orig_param_name + " " + param_value_parsed_object.value)
                else:
                    pnl.type = "COMMENT"
                    pnl.name = ".OPTIONS " + orig_param_name
                    if "COMMENT" in pnl.params_dict:
                        pnl.add_comment(pnl.params_dict["COMMENT"] + " " + ".OPTIONS " + orig_param_name + " " + param_value_parsed_object.value)
                    else:
                        pnl.add_comment(".OPTIONS " + orig_param_name + " " + param_value_parsed_object.value)


        elif parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME and parsed_object.value.upper() == ".IF":

            pnl.type = "COMMENT"
            pnl.add_comment(parsed_object.value)

            self._if_statement = True
            self._nested_if_statement_count += 1


        elif parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME and parsed_object.value.upper() == ".ELSEIF":

            pnl.type = "COMMENT"
            pnl.add_comment(parsed_object.value)


        elif parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME and parsed_object.value.upper() == ".ELSE":

            pnl.type = "COMMENT"
            pnl.add_comment(parsed_object.value)


        elif parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME and parsed_object.value.upper() == ".ENDIF":

            pnl.type = "COMMENT"
            pnl.add_comment(parsed_object.value)

            self._nested_if_statement_count -= 1
            if self._nested_if_statement_count == 0:
                self._if_statement = False
                self._comment_end_of_if_statement = True


        elif parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME and parsed_object.value.upper() == ".MACRO":
            pnl.type = ".SUBCKT"


        elif parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME and parsed_object.value.upper() == ".EOM":
            pnl.type = ".ENDS"


        elif parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME and parsed_object.value.upper() == ".MEAS":
            pnl.type = ".MEASURE"


        elif parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME and (parsed_object.value.upper() == ".TEMP" or parsed_object.value.upper() == ".TEMPERATURE"):
            pnl.type = parsed_object.value.upper()
            pnl.local_type = parsed_object.value.upper()
            self._temp_defined = True


        elif parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME and parsed_object.value.upper() == ".PROBE" or parsed_object.value.upper() == ".PROBE64":
            pnl.type = ".PRINT"
            pnl.add_known_object("TRAN", Types.analysisTypeValue)  # default tran type


        elif parsed_object.types[0] == SpiritCommon.data_model_type.OUTPUT_VARIABLE:

            #remove [] from HSPICE print variables -- eventually this will be replaced in the writer
            output_variable_clean = self.clean_hspice_output_variable(parsed_object.value)

            pnl.add_output_variable_value(output_variable_clean)


        elif parsed_object.types[0] == SpiritCommon.data_model_type.MODEL_TYPE and pnl.type == ".MODEL":

            # convert hspice type into the general type supported by the ADM
            adm_type = hspice_to_adm_model_type_map.get(parsed_object.value.upper())

            # if not mapped, then use current value
            if not adm_type:
                adm_type = parsed_object.value.upper()

            pnl.add_known_object(adm_type, Types.modelType)

            # create a pnl for model binning option
            if "." in pnl.name:
                pnl_synth = ParsedNetlistLine(pnl.filename, [0])  # what to do with line numbers?
                pnl_synth.type = ".OPTIONS"
                pnl_synth.local_type = ".OPTIONS"
                pnl_synth.add_known_object("PARSER", Types.optionPkgTypeValue)
                pnl_synth.add_param_value_pair("model_binning", "true")
                pnl_synth.flag_top_pnl = True
                synthesized_pnls.append(pnl_synth)


        elif parsed_object.types[0] == SpiritCommon.data_model_type.GENERALNODE and not pnl.type in [".IC", ".DCVOLT", ".NODESET"]:

            if BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]] in pnl.known_objects and pnl.type == ".GLOBAL":
                pnl_synth = ParsedNetlistLine(pnl.filename, pnl.linenum)
                pnl_synth.type = ".GLOBAL"
                pnl_synth.local_type = ".GLOBAL"
                pnl_synth.add_known_object(parsed_object.value, BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]])
                synthesized_pnls.append(pnl_synth)
            else:
                pnl.add_known_object(parsed_object.value, BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]])


        elif parsed_object.types[0] == SpiritCommon.data_model_type.GENERALNODE and pnl.type in [".IC", ".DCVOLT", ".NODESET"]:
            if not pnl.initial_conditions_list:
                initial_condition_dict = {}
                initial_condition_dict[Types.voltageOrCurrent] = "V"
                initial_condition_dict[Types.generalNodeName] = parsed_object.value
                pnl.initial_conditions_list.append(initial_condition_dict)
                
            elif Types.generalNodeName in pnl.initial_conditions_list[-1]:
                initial_condition_dict = {}
                initial_condition_dict[Types.voltageOrCurrent] = "V"
                initial_condition_dict[Types.generalNodeName] = parsed_object.value
                pnl.initial_conditions_list.append(initial_condition_dict)

            else:
                pnl.initial_conditions_list[-1][Types.generalNodeName] = parsed_object.value


        elif parsed_object.types[0] == SpiritCommon.data_model_type.FUNC_NAME_VALUE:
            # For lines with mixed parameter and function statements in HSPICE, separate them out
            # into different ParsedNetlistLine objects and store it in synthesized pnl 
            if pnl.params_dict or "FUNC_EXPRESSION" in pnl.known_objects:
                pnl_synth = ParsedNetlistLine(pnl.filename, pnl.linenum)  # what to do with line numbers?
                pnl_synth.type = ".FUNC"
                pnl_synth.local_type = ".FUNC"
                pnl_synth.add_known_object(parsed_object.value, BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]])
                func_arg_parsed_object = next(parsed_object_iter)
                while func_arg_parsed_object.types[0] == SpiritCommon.data_model_type.FUNC_ARG_VALUE:
                    pnl_synth.add_func_arg_value(func_arg_parsed_object.value)
                    func_arg_parsed_object = next(parsed_object_iter)
                func_expression_parsed_object = func_arg_parsed_object

                processed_value = self.hack_ternary_operator(func_expression_parsed_object.value)
                processed_value = self.hack_exponentiation_symbol(processed_value)

                pnl_synth.add_known_object(processed_value, BoostParserInterface.boost_xdm_map_dict[func_expression_parsed_object.types[0]])
                synthesized_pnls.append(pnl_synth)
            else:
                pnl.type = ".FUNC"
                pnl.local_type = ".FUNC"
                pnl.add_known_object(parsed_object.value, BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]])
                func_arg_parsed_object = next(parsed_object_iter)
                while func_arg_parsed_object.types[0] == SpiritCommon.data_model_type.FUNC_ARG_VALUE:
                    pnl.add_func_arg_value(func_arg_parsed_object.value)
                    func_arg_parsed_object = next(parsed_object_iter)
                func_expression_parsed_object = func_arg_parsed_object

                processed_value = self.hack_ternary_operator(func_expression_parsed_object.value)
                processed_value = self.hack_exponentiation_symbol(processed_value)

                pnl.add_known_object(processed_value, BoostParserInterface.boost_xdm_map_dict[func_expression_parsed_object.types[0]])


        elif parsed_object.types[0] == SpiritCommon.data_model_type.PARAM_NAME:

            param_value_parsed_object = next(parsed_object_iter)

            if param_value_parsed_object.types[0] != SpiritCommon.data_model_type.PARAM_VALUE:
                logging.error(
                    "Line(s):" + str(pnl.linenum) + ". Parser passed wrong token.  Expected PARAM_VALUE.  Got " + str(
                        param_value_parsed_object.types[0]))
                raise Exception("Next Token is not a PARAM_VALUE.  Something went wrong!")

            if pnl.type == ".FUNC":
                # Same as above, for lines with mixed parameter and function statements in HSPICE, separate them out
                # into different ParsedNetlistLine objects and store it in synthesized pnl 
                if synthesized_pnls:
                    processed_value = self.hack_ternary_operator(param_value_parsed_object.value)
                    processed_value = self.hack_exponentiation_symbol(processed_value)

                    synthesized_pnls[-1].add_param_value_pair(parsed_object.value.upper(), processed_value)
                else:
                    pnl_synth = ParsedNetlistLine(pnl.filename, pnl.linenum)  # what to do with line numbers?
                    pnl_synth.type = ".PARAM"
                    pnl_synth.local_type = ".PARAM"

                    processed_value = self.hack_ternary_operator(param_value_parsed_object.value)
                    processed_value = self.hack_exponentiation_symbol(processed_value)

                    pnl_synth.add_param_value_pair(parsed_object.value.upper(), processed_value)
                    synthesized_pnls.append(pnl_synth)
            else:
                processed_value = self.hack_ternary_operator(param_value_parsed_object.value)
                if pnl.type in [".PARAM", ".SUBCKT", ".MODEL", ".MACRO", ".GLOBAL_PARAM"] or pnl.type in supported_devices:
                    processed_value = self.curly_braces_for_expressions(processed_value)
                processed_value = self.hack_exponentiation_symbol(processed_value)

                pnl.add_param_value_pair(parsed_object.value.upper(), processed_value)


        elif parsed_object.types[0] == SpiritCommon.data_model_type.PARAM_VALUE and pnl.params_dict:
            # Same as above, for lines with mixed parameter and function statements in HSPICE, separate them out
            # into different ParsedNetlistLine objects and store it in synthesized pnl 
            if pnl.type == ".FUNC":
                last_key = synthesized_pnls[-1].params_dict.keys()[-1]
                prev_param_value = synthesized_pnls[-1].params_dict[last_key]

                processed_value = self.hack_ternary_operator(parsed_object.value)
                processed_value = self.hack_exponentiation_symbol(processed_value)

                synthesized_pnls[-1].params_dict[last_key] = prev_param_value+" "+processed_value

            else:
                last_key = pnl.params_dict.keys()[-1]
                prev_param_value = pnl.params_dict[last_key]

                processed_value = self.hack_ternary_operator(parsed_object.value)


                if pnl.type in [".PARAM", ".SUBCKT", ".MODEL", ".MACRO", ".GLOBAL_PARAM"] or pnl.type in supported_devices:
                    processed_value = self.curly_braces_for_expressions(processed_value)


                processed_value = self.hack_exponentiation_symbol(processed_value)

                pnl.params_dict[last_key] = prev_param_value+" "+processed_value


        elif parsed_object.types[0] == SpiritCommon.data_model_type.COMMENT:

            pnl.type = "COMMENT"


            if parsed_object.value.startswith("//"):
                pnl.name = parsed_object.value[2:]
                pnl.add_comment(parsed_object.value[2:])

            else:
                pnl.name = parsed_object.value[1:]
                pnl.add_comment(parsed_object.value[1:])


        elif parsed_object.types == [SpiritCommon.data_model_type.MODEL_NAME, SpiritCommon.data_model_type.VALUE]:
            lst = []
            for typ in parsed_object.types:
                lst.append(BoostParserInterface.boost_xdm_map_dict[typ])

            processed_value = self.hack_ternary_operator(parsed_object.value)
            processed_value = self.hack_exponentiation_symbol(processed_value)

            pnl.add_lazy_statement(processed_value, lst)
         

        elif parsed_object.types[0] in [SpiritCommon.data_model_type.DC_VALUE_VALUE, SpiritCommon.data_model_type.AC_MAG_VALUE, SpiritCommon.data_model_type.AC_PHASE_VALUE]:
            processed_value = self.curly_braces_for_expressions(parsed_object.value)
            
            pnl.add_known_object(processed_value, BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]])


        elif parsed_object.types[0] == SpiritCommon.data_model_type.DATA_TABLE_NAME:


            if pnl.type == ".DATA":
                pnl.add_known_object(parsed_object.value, BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]])

            elif pnl.type == ".TRAN":
                pnl_synth = ParsedNetlistLine(pnl.filename, pnl.linenum)
                pnl_synth.type = ".STEP"
                pnl_synth.local_type = ".STEP"

                pnl_synth.add_sweep_param_value("DATA")
                pnl_synth.add_sweep_param_value(parsed_object.value)
                synthesized_pnls.append(pnl_synth)

            elif pnl.type == ".DC" or pnl.type == ".AC":
                pnl.add_sweep_param_value("DATA")
                pnl.add_sweep_param_value(parsed_object.value)


        elif parsed_object.types[0] == SpiritCommon.data_model_type.TRANS_REF_NAME:
            processed_value = self.curly_braces_for_expressions(parsed_object.value)
            pnl.add_transient_value(processed_value)


        elif parsed_object.types[0] == SpiritCommon.data_model_type.CONDITIONAL_STATEMENT:

            comment = pnl.params_dict[Types.comment] + parsed_object.value
            pnl.add_comment(comment)


        elif parsed_object.types[0] == SpiritCommon.data_model_type.SWEEP_TYPE and pnl.type == ".DC":

            pnl.sweep_param_list.insert(-1, parsed_object.value)
            self._data_driven = True


        elif parsed_object.types[0] == SpiritCommon.data_model_type.SWEEP_PARAM_VALUE and self._data_driven:

            if self._np < 0:
                self._np = int(parsed_object.value)

            else:
                pnl.add_sweep_param_value(parsed_object.value)

                if len(pnl.sweep_param_list) > 3:

                    if pnl.sweep_param_list[-4].upper() == "LIN":
                        incr = (float(pnl.sweep_param_list[-2]) + float(pnl.sweep_param_list[-1])) / (self._np - 1)
                        pnl.add_sweep_param_value("%g" % incr)

                        self._data_driven = False
                        self._np = -1

                    elif pnl.sweep_param_list[-4].upper() in ["DEC", "OCT"]:
                        pnl.add_sweep_param_value("%s" % self._np)

                        self._data_driven = False
                        self._np = -1


        else:
            XyceNetlistBoostParserInterface.convert_next_token(parsed_object, parsed_object_iter, pnl, synthesized_pnls)


    @staticmethod
    def clean_hspice_output_variable(in_output_variable):
        """
        In Output Variables, removes brackets, converts N to V, and IA/IB to I1/I2
        """

        out_output_variable = in_output_variable.replace("[", "")
        out_output_variable = out_output_variable.replace("]", "")
        out_output_variable = out_output_variable.replace("N(", "V(")
        out_output_variable = out_output_variable.replace("IA(", "I1(")
        out_output_variable = out_output_variable.replace("IB(", "I2(")

        return out_output_variable


    @staticmethod
    def hack_ternary_operator(in_expression):
        """
        Hack to place in empty space to left of colons in presumed ternary operators
        """

        q_list = []
        out_expression = ""

        # first check ternary operator is in expression
        if "?" in in_expression and ":" in in_expression:

            # Next, make sure every "?" is followed by a ":" and that there are equal number of each.
            # If not, give warning, return the expression, and continue translating. 
            # TODO: figure out if it's better to comment out? might not be, since expression may be 
            #       on a line containing multiple expressions, which would end up commenting out everything
            #       else
            for char in in_expression:
                if char == "?":
                    q_list.append(char)
                    out_expression += char
                elif char == ":":
                    if not q_list:
                        logging.warning("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(pnl.linenum) + ". Ternary operator cannot be translated. Continuing.")
                        return in_expression
                    else:
                        q_list.pop()

                        # if there's an empty space to the left of ":", no need to add another
                        if out_expression[-1] == " ":
                            out_expression += char
                        else:
                            out_expression += " "+char
                else:
                    out_expression += char

            if q_list:
                logging.warning("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(pnl.linenum) + ". Ternary operator cannot be translated. Continuing.")
                return in_expression 
                
        # if no ternary operator in expression, return expression unchanged
        else:
            return in_expression

        return out_expression


    @staticmethod
    def curly_braces_for_expressions(in_expression):
        """
        Enclose expressions in curly braces for Xyce.
        """

        # first check if expression is already enclosed in single quotes, which is legal in Xyce.
        # if so, just return expression
        if in_expression.startswith("'") and in_expression.endswith("'"):
            return in_expression

        # remove single quotes that may be around function arguments
        expression_fields = in_expression.split("'")
        out_expression = "".join(expression_fields)

        # find expression components. put braces around everything - only exception is if it is a
        # number
        expr_components = []
        expr_utils.find_expr_components(out_expression, [], expr_components)

        if ((len(expr_components) == 1 and expr_components[0].types[0] == SpiritExprCommon.expr_data_model_type.NUMBER) or
           (len(expr_components) == 2 and (expr_components[0].types[0] == SpiritExprCommon.expr_data_model_type.NUMBER and
           (expr_components[1].types[0] == SpiritExprCommon.expr_data_model_type.UNARY_NEG or 
           expr_components[1].types[0] == SpiritExprCommon.expr_data_model_type.UNARY_POS))) or 
           len(expr_components) == 0):
            return out_expression

        out_expression = "{" + out_expression + "}"

        return out_expression


    @staticmethod
    def hack_exponentiation_symbol(in_expression):
        """
        Hack to translate "^" math symbol to "**"
        """

        out_expression = in_expression.replace("^", "**")

        return out_expression


    @staticmethod
    def hack_packages_bugzilla_2020(param, pkgs):
        """
        Hack for package conversion
        """
        result_param = param
        result_pkgs = pkgs
        if param == "ITL1":
            logging.info("Converting ITL1 into NONLIN MAXSTEP")
            result_param = "MAXSTEP"
            result_pkgs = ["NONLIN"]
        elif param == "ITL4":
            logging.info("Converting ITL4 into NONLIN-TRAN MAXSTEP")
            result_param = "MAXSTEP"
            result_pkgs = ["NONLIN-TRAN"]
        elif param == "ABSTOL": # HSPICE ABSTOL is not Xyce ABSTOL
            logging.info("Removing ABSTOL.  hspice ABSTOL is not the equivalent of Xyce ABSTOL")
            result_param = None
            result_pkgs = []
        elif param == "VNTOL":
            logging.info("Converting VNTOL into NONLIN/NONLIN-TRAN ABSTOL")
            result_param = "ABSTOL"
            result_pkgs = ["NONLIN", "NONLIN-TRAN"]
        return result_param, result_pkgs

    @staticmethod
    def get_default(param):
        """
        Hack for undefined values
        """
        return_value = ""
        if default_values.get(param):
            return_value = default_values[param]
        return return_value

    @property
    def tnom_defined(self):
        return self._tnom_defined

    @property
    def tnom_value(self):
        return self._tnom_value

    @property
    def temp_defined(self):
        return self._temp_defined
