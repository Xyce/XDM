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
from xdm.inout.readers.XyceNetlistBoostParserInterface import XyceNetlistBoostParserInterface

spectre_to_adm_model_type_map = {"resistor": "R", "capacitor": "C", "diode": "D", "inductor": "L",
                                 "mutual_inductor": "K", "gaas": "Z", "tline": "T", "vcvs": "E", "vccs": "G",
                                 "pvcvs": "E", "pvccs": "G", "vsource": "V", "isource": "I", "jfet": "J", "mos1": "M",
                                 "bsim3v3": "M", "mos902": "M", "bsimsoi": "M", "bsim4": "M", "bsimcmg": "M",
                                 "model": ".MODEL", "parameters": ".PARAM", "port": "P",
                                 "bjt": "Q", "vbic": "Q",
                                 "subckt": ".SUBCKT", "ends": ".ENDS", "include": ".INCLUDE", "section": ".LIB",
                                 "endsection": ".ENDL", "ac": ".AC", "alter": "alter", "altergroup": "altergroup",
                                 "check": "check", "checklimit": "checklimit", "cosim": "cosim", "dc": ".DC",
                                 "dcmatch": "dcmatch", "envlp": "envlp", "hb": "hb", "hbac": "hbac",
                                 "hbnoise": "hbnoise", "hbsp": "hbsp", "info": "info", "loadpull": "loadpull",
                                 "montecarlo": "montecarlo", "noise": "noise", "options": "options", "pac": "pac",
                                 "pdisto": "pdisto", "pnoise": "pnoise", "psp": "psp", "pss": "pss", "pstb": "pstb",
                                 "pxf": "pxf", "pz": "pz", "qpac": "qpac", "qpnoise": "qpnoise", "qpsp": "qpsp",
                                 "qpss": "qpss", "qpxf": "qpxf", "reliability": "reliability", "set": "set",
                                 "shell": "shell", "sp": "sp", "stb": "stb", "sweep": "sweep", "tdr": "tdr",
                                 "tran": ".TRAN", "uti": "uti", "xf": "xf", "analogmodel": "analogmodel",
                                 "bsource": "B", "checkpoint": "checkpoint", "smiconfig": "smiconfig",
                                 "constants": "constants", "convergence": "convergence", "encryption": "encryption",
                                 "expressions": "expressions", "functions": "functions", "global": ".GLOBAL",
                                 "ibis": "ibis", "ic": "ic", "if": "if", "keywords": "keywords", "memory": "memory",
                                 "nodeset": "nodeset", "param_limits": "param_limits", "paramset": "paramset",
                                 "real": ".FUNC", "rfmemory": "rfmemory", "save": ".PRINT", "savestate": "savestate",
                                 "sens": "sens", "spectrerf": "spectrerf", "stitch": "stitch", "vector": "vector",
                                 "veriloga": "veriloga", "simulator": "simulator", "library": "library",
                                 "endlibrary": "endlibrary", "modelParameter": "modelParameter",
                                 "simulatorOptions": "simulatorOptions", "finalTimeOP": "finalTimeOP",
                                 "element": "element", "outputParameter": "outputParameter",
                                 "designParamVals": "designParamVals", "primitives": "primitives", "subckts": "subckts",
                                 "saveOptions": "saveOptions"}

spectre_tran_param_type = {
    "step": Types.printStepValue,
    "stop": Types.finalTimeValue
}

def format_output_variable(input_string):
    result = input_string
    if "(" not in input_string:
        if ":1" in input_string:
            result = "I(" + input_string + ")"
            result = result.replace(":1", "")
        else:
            result = "V(" + input_string + ")"

    if "{" not in result:
        result = result.replace(".", ":")
    return result


def is_a_number(in_expression):
    """
    Checks to see if expression is number
    """

    # if the input is enclosed in parentheses, even if it's just a number, Xyce will consider
    # it as an expression. 
    if "(" in in_expression:
        return False

    # find expression components. put braces around everything - only exception is if it is a
    # number
    expr_components = []
    expr_utils.find_expr_components(in_expression, [], expr_components, lang="spectre")

    if ((len(expr_components) == 1 and expr_components[0].types[0] == SpiritExprCommon.expr_data_model_type.NUMBER) or
       (len(expr_components) == 2 and (expr_components[0].types[0] == SpiritExprCommon.expr_data_model_type.NUMBER and
       (expr_components[1].types[0] == SpiritExprCommon.expr_data_model_type.UNARY_NEG or 
       expr_components[1].types[0] == SpiritExprCommon.expr_data_model_type.UNARY_POS)))):
        return True

    return False


def convert_si_unit_prefix(in_expression):
    """
    Converts SI unit prefix M (for mega) in Spectre to
    X (for mega) in Xyce
    """

    prefix_ind = -1

    # case for number having unit prefix and unit, i.e. 10uH
    if len(in_expression) > 2:

        if in_expression[-2].isalpha():

            prefix_ind = -2
            pass

    if in_expression[prefix_ind] == "M":

        out_expression = list(in_expression)
        out_expression[prefix_ind] = "x"
        out_expression = ''.join(out_expression)

    elif in_expression[prefix_ind] == "a":

        out_expression = list(in_expression)
        out_expression[prefix_ind] = "e-18"
        out_expression = ''.join(out_expression)

    else:

        out_expression = in_expression

    return out_expression


def convert_to_xyce(expression):
    """
    split on anything we want to convert or identify as legal or illegal
    in Xyce. If a token is illegal it should raise an warning in XDM. If a token
    is legal in Xyce then the expression that contains it should be surrounded
    by {}. If a token is converted to something legal in Xyce, then it the
    expression that contains it should be surrounded by {}. msg should be set
    to the warning message, if any, and that should trigger a
    logging.warning(...) call. This call is up to the caller of this functions.
    """

    # seen in a PDK - semicolons at the end of the line. Not sure if this is 
    # acutally allowed in Spectre, or if it is a bug in a PDK.
    expression = expression.strip(";")

    # Only set msg if there's an error
    msg = ""

    # Skip this whole dirty hack if original input is just a number
    if is_a_number(expression):
        expression = convert_si_unit_prefix(expression)
        return expression, msg

    # Split the expression string by all operators. Examine for validity
    # or conversion to Xyce
    tokens = (
        "(\(|\+|-|\*\*|\*|\/|&&|&|==|<<|<|>>|>|<=|>=|\|\||\||\?|:|,|\))")
    split = re.split(tokens, expression.replace(" ", ""))

    # convert Spectre boolean operators to their Xyce counterparts
    # convert Spectre functions to uppercase
    # convert spectre constants to numeric values
    spectre_to_xyce = {"M_PI_4": "0.78539816339744830962", "M_PI_2": "1.57079632679489661923",
                       "M_PI": "3.14159265358979323846", "M_1_PI": "0.31830988618379067154",
                       "M_2_PI": "0.63661977236758134308", "M_2_SQRTPI": "1.12837916709551257390",
                       "M_DEGPERRAD": "57.2957795130823208772", "M_E": "2.7182818284590452354",
                       "M_LN10": "2.30258509299404568402", "M_LN2": "0.69314718055994530942",
                       "M_LOG10E": "0.43429448190325182765", "M_LOG2E": "1.4426950408889634074",
                       "M_SQRT1_2": "0.70710678118654752440", "M_SQRT2": "1.4142135623730950488",
                       "M_TWO_PI": "6.28318530717958647652", "P_C": "2.997924562e8", "P_H": "6.6260755e-34",
                       "P_K": "1.3806226e-23", "P_Q": "1.6021918e-19", "||": "|", "&&": "&", "<<": "<", ">>": ">",
                       "log": "LOG", "log10": "LOG10", "exp": "EXP", "sqrt": "SQRT", "min": "MIN", "max": "MAX",
                       "abs": "ABS", "pow": "POW", "int": "INT", "sin": "SIN", "tanh": "TANH", "tan": "TAN",
                       "sinh": "SINH", "cosh": "COSH", "cos": "COS", "atanh": "ATANH", "atan2": "ATAN2", "atan": "ATAN",
                       "asinh": "ASINH", "asin": "ASIN", "acosh": "ACOSH", "acos": "ACOS"}

    valid_xyce_ops = ["+", "-", "**", "*", "/", "~", "|", "&", "==", "!=", ">", ">=", ">", ">="]
    # These are invalid in Xyce
    # invalid_ops = ["&", "|", "~^", "^~"]

    # These functions aren't available in Xyce
    # invalid_ftns = ["hypot", "ceil", "floor", "fmod", "?"]
    for i, token in enumerate(split):
        # Find things that can't be converted to xyce
        # These are currently caught by the boost parser
        # if token in invalid_ops:
        # msg = "Spectre expression constaints bitwise operator " + token + " not available in Xyce."
        # return None, msg
        # Find things that can't be converted to xyce
        # These are currently caught by the boost parser
        # if token in invalid_ftns:
        # msg = "Spectre expression contains function" + token + " not available in Xyce."
        # return None, msg

        # convert what we can
        # id = spectre_tran_param_type
        if not token:
            continue
        elif token in spectre_to_xyce:
            split[i] = spectre_to_xyce[token]
        elif token in valid_xyce_ops:
            continue
        else:
            if is_a_number(token):
                split[i] = convert_si_unit_prefix(token)



    # Check one more time if expression is just a number, which
    # would be the case if it's just a built in constant. If it
    # is, no brackets needed.
    out_expression = "".join(split)
    if not is_a_number(out_expression):
        out_expression = "{" + out_expression + "}"

    return out_expression, msg


class SpectreNetlistBoostParserInterface(object):
    """
    Allows for Spectre to be read in using the Boost Parser.  Iterates over
    statements within the Spectre netlist file.
    """

    def __init__(self, filename, language_definition, top_level_file=True):
        self.internal_parser = SpiritCommon.SpectreNetlistBoostParser()
        self.goodfile = self.internal_parser.open(filename, top_level_file)
        self.line_iter = iter(self.internal_parser)
        self._filename = filename
        self._language_definition = language_definition
        self._top_level_file = top_level_file
        self._tnom_defined = False
        self._temp_defined = False
        self._tnom_value = "27"

        # Flag to indicate delimited block
        self._delimited_block = False
        self._delimited_directives = [".FUNC", ".MODEL"]

        # Comment out IF statements and any conditional block for it for now
        self._if_statement = False
        self._comment_end_of_if_statement = False

        # flag to indicate modifications should be to last synthesized pnl in stack
        self._modify_synth_pnl = False
        self._write_model_binning_option = False

        if not self.goodfile:
            logging.error("File: " + filename + " was not found. Please locate this file and try again.\n\n\n")
            sys.exit(1)

        # a list of parsed netlist line objects created during conversion to adm
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
            self.convert_next_token(parsedObject, parsed_object_iter, pnl, self._synthesized_pnls)

        # Hack for if statements - comment out line
        if self._if_statement:
            pnl.add_comment(boost_parsed_line.sourceline)
            logging.warning("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(pnl.linenum) + ". If statement cannot be translated. Continuing.")

        if self._comment_end_of_if_statement:
            pnl.type = "COMMENT"
            pnl.add_comment(boost_parsed_line.sourceline)
            self._comment_end_of_if_statement = False
            logging.warning("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(pnl.linenum) + ". If statement cannot be translated. Continuing.")

        # Lookahead for directives that may include curly brace delimited blocks
        boost_parsed_line_next = ""
        if (pnl.type in self._delimited_directives or pnl.local_type == "if") and not self._delimited_block:
            try:
                boost_parsed_line_next = next(self.line_iter)

                pnl_next = ParsedNetlistLine(boost_parsed_line_next.filename, boost_parsed_line_next.linenums)

                parsed_object_iter = iter(boost_parsed_line_next.parsed_objects)

                for parsedObject in parsed_object_iter:
                    self.convert_next_token(parsedObject, parsed_object_iter, pnl_next, self._synthesized_pnls)

                    if self._delimited_block:
                        if self._if_statement:
                            pnl_synth = ParsedNetlistLine(boost_parsed_line_next.filename, boost_parsed_line_next.linenums)
                            pnl_synth.type = "COMMENT"
                            pnl_synth.add_comment(boost_parsed_line_next.sourceline)
                            self._synthesized_pnls.append(pnl_synth)
                            logging.warning("In file:\"" + str(os.path.basename(pnl_synth.filename)) + "\" at line:" + str(pnl_synth.linenum) + ". If statement cannot be translated. Continuing.")
                            
                        break

                # If block delimiter is not detected, the next line is just the next
                # statement, and it will be added to synthesized pnl to be processed
                # as normally.
                if not self._delimited_block and pnl_next.type:
                    self._synthesized_pnls.append(pnl_next)

            except:
                pass

        # if it is a delimited block, continue processing with the current pnl
        curr_pnl = pnl
        while self._delimited_block:
            # Does not apply to IF statement blocks
            if self._if_statement:
                break

            if not boost_parsed_line_next:
                boost_parsed_line_next = next(self.line_iter)

            curr_pnl.linenum.extend(boost_parsed_line_next.linenums)

            parsed_object_iter = iter(boost_parsed_line_next.parsed_objects)

            for parsedObject in parsed_object_iter:
                self.convert_next_token(parsedObject, parsed_object_iter, curr_pnl, self._synthesized_pnls)

                # for binned models, if new binned model is encountered, start
                # modifying that
                if self._modify_synth_pnl:
                    curr_pnl = self._synthesized_pnls[-1]
                    self._modify_synth_pnl = False

            boost_parsed_line_next = ""

        if len(pnl.source_params) > 0:
            self._handle_source_params(pnl)

        if not silent:
            if boost_parsed_line.error_type == "critical":
                pnl.error_type = boost_parsed_line.error_type
                pnl.error_message = boost_parsed_line.error_message
                logging.critical("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(
                    pnl.linenum) + ". " + boost_parsed_line.error_message)
            elif boost_parsed_line.error_type == "error":
                pnl.error_type = boost_parsed_line.error_type
                pnl.error_message = boost_parsed_line.error_message
                logging.error("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(
                    pnl.linenum) + ". " + boost_parsed_line.error_message)
            elif boost_parsed_line.error_type == "warn":
                pnl.error_type = boost_parsed_line.error_type
                pnl.error_message = boost_parsed_line.error_message
                logging.warning("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(
                    pnl.linenum) + ". " + boost_parsed_line.error_message)
            elif boost_parsed_line.error_type == "info":
                pnl.error_type = boost_parsed_line.error_type
                pnl.error_message = boost_parsed_line.error_message
                logging.info("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(
                    pnl.linenum) + ". " + boost_parsed_line.error_message)
            else:
                pnl.error_type = " "

        return pnl

    @staticmethod
    def _handle_source_params(pnl):
        """
        Maps known source params to appropriate transient types
        """
        if pnl.source_params.get("type"):
            if pnl.source_params["type"] == "sine":
                pnl.add_known_object("SIN", Types.trans_func)
                if pnl.source_params.get("sinedc"):
                    pnl.add_transient_value(pnl.source_params["sinedc"])
                else:
                    pnl.add_transient_value("0")
                if pnl.source_params.get("ampl"):
                    pnl.add_transient_value(pnl.source_params["ampl"])
                else:
                    pnl.add_transient_value("1")
                if pnl.source_params.get("freq"):
                    pnl.add_transient_value(pnl.source_params["freq"])
                else:
                    pnl.add_transient_value("0")
                if pnl.source_params.get("delay"):
                    pnl.add_transient_value(pnl.source_params["delay"])
                else:
                    pnl.add_transient_value("0")
                if pnl.source_params.get("damp"):
                    pnl.add_transient_value(pnl.source_params["damp"])
                else:
                    pnl.add_transient_value("0")
                if pnl.source_params.get("sinephase"):
                    pnl.add_transient_value(pnl.source_params["sinephase"])
                else:
                    pnl.add_transient_value("0")

            elif pnl.source_params["type"] == "exp":
                pnl.add_known_object("EXP", Types.trans_func)
                if pnl.source_params.get("val0"):
                    pnl.add_transient_value(pnl.source_params["val0"])
                else:
                    pnl.add_transient_value("0")
                if pnl.source_params.get("val1"):
                    pnl.add_transient_value(pnl.source_params["val1"])
                else:
                    pnl.add_transient_value("1")
                if pnl.source_params.get("td1"):
                    pnl.add_transient_value(pnl.source_params["td1"])
                else:
                    pnl.add_transient_value("0")
                if pnl.source_params.get("tau1"):
                    pnl.add_transient_value(pnl.source_params["tau1"])
                else:
                    pnl.add_transient_value("0")
                if pnl.source_params.get("td2"):
                    pnl.add_transient_value(pnl.source_params["td2"])
                else:
                    pnl.add_transient_value("0")
                if pnl.source_params.get("tau2"):
                    pnl.add_transient_value(pnl.source_params["tau2"])
                else:
                    pnl.add_transient_value("0")

            elif pnl.source_params["type"] == "pulse":
                pnl.add_known_object("PULSE", Types.trans_func)
                if pnl.source_params.get("val0"):
                    pnl.add_transient_value(pnl.source_params["val0"])
                else:
                    pnl.add_transient_value("0")
                if pnl.source_params.get("val1"):
                    pnl.add_transient_value(pnl.source_params["val1"])
                else:
                    pnl.add_transient_value("1")
                if pnl.source_params.get("delay"):
                    pnl.add_transient_value(pnl.source_params["delay"])
                else:
                    pnl.add_transient_value("0")
                if pnl.source_params.get("rise"):
                    pnl.add_transient_value(pnl.source_params["rise"])
                else:
                    pnl.add_transient_value("0")
                if pnl.source_params.get("fall"):
                    pnl.add_transient_value(pnl.source_params["fall"])
                else:
                    pnl.add_transient_value("0")
                if pnl.source_params.get("width"):
                    pnl.add_transient_value(pnl.source_params["width"])
                else:
                    pnl.add_transient_value("0")
                if pnl.source_params.get("period"):
                    pnl.add_transient_value(pnl.source_params["period"])
                else:
                    pnl.add_transient_value("0")

            elif pnl.source_params["type"] == "pwl":
                pnl.add_known_object("PWL", Types.trans_func)
                if pnl.source_params.get("file"):
                    pnl.add_transient_value("FILE")
                    pnl.add_transient_value(pnl.source_params["file"])
                if pnl.source_params.get("delay"):
                    pnl.add_param_value_pair("delay", pnl.source_params["delay"])

        # source_params_deleted = {"type", "dc", "sinedc", "ampl", "freq", "delay", "damp", "phase", "val0", "val1",
        #                          "td1", "tau1", "td2", "tau2", "rise", "fall", "width", "period", "file" }
        # for key in source_params_deleted:
        #     if key in self._source_params:
        #         del self._source_params[key]
        #
        # for key, value in self._source_params.iteritems():
        #     pnl.add_param_value_pair(key, value)

    @staticmethod
    def set_tran_param(pnl, param_key, param_value):
        """
        Maps known tran params
        """
        if spectre_tran_param_type.get(param_key):
            if not param_value.endswith("s"):
                param_value = param_value + "s"
            pnl.add_known_object(param_value, spectre_tran_param_type[param_key])
        else:
            logging.warning(
                "Unsupported parameter in spectre tran statement: " + param_key + " Line(s): " + str(pnl.linenum))

    def convert_next_token(self, parsed_object, parsed_object_iter, pnl, synthesized_pnls):
        """
        Takes individual parsed objects from the parsed line object

        Populate ParsedNetlistLine class with all information necessary to create a Statement

        Many hacks contained here
        """

        if parsed_object.types[0] == SpiritCommon.data_model_type.BLOCK_DELIMITER:

            if parsed_object.value == "{":

                self._delimited_block = True

            else:
                self._delimited_block = False

                if self._if_statement:

                    self._if_statement = False
                    self._comment_end_of_if_statement = True


        elif self._if_statement:

            pnl.type = "COMMENT"
            

        elif parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME or parsed_object.types[
            0] == SpiritCommon.data_model_type.DEVICE_TYPE:

            if spectre_to_adm_model_type_map.get(parsed_object.value):

                pnl.type = spectre_to_adm_model_type_map[parsed_object.value]
                pnl.local_type = parsed_object.value

            else:

                logging.warning("Possible error. Spectre type not recognized: " + str(parsed_object.value))

            # If directive is .GLOBAL, for now get rid of first listed node. This first node is
            # considered a ground node.
            if pnl.type == ".GLOBAL":

                next(parsed_object_iter)

            if pnl.type == "if":

                pnl.type = "COMMENT"
                pnl.add_comment(parsed_object.value)

                self._if_statement = True

        elif parsed_object.types[0] == SpiritCommon.data_model_type.MODEL_NAME and not pnl.type == ".MODEL":

            if spectre_to_adm_model_type_map.get(parsed_object.value):

                pnl.type = spectre_to_adm_model_type_map[parsed_object.value]
                pnl.local_type = parsed_object.value

            else:

                pnl.add_known_object(parsed_object.value, Types.modelName)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.MODEL_TYPE and pnl.type == ".MODEL":

            adm_type = spectre_to_adm_model_type_map.get(parsed_object.value)

            # For Spectre, different models aren't distinguished by a "LEVEL" parameter. Instead,
            # it uses a name to distinguish what model is being used (ex., bsimsoi instead of
            # LEVEL=10, or vbic instead of LEVEL=10).
            if adm_type == "M" or adm_type == "Q" or adm_type == "J":

                pnl.add_param_value_pair("LEVEL", parsed_object.value)

            if not adm_type:

                adm_type = parsed_object.value


            # Default to NMOS for type
            if adm_type == "M":

                pnl.add_known_object("NMOS", Types.modelType)
                pnl.add_param_value_pair("type", "N")

            elif adm_type == "J":

                pnl.add_known_object("NJF", Types.modelType)
                pnl.add_param_value_pair("type", "N")

            else:

                pnl.add_known_object(adm_type, Types.modelType)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.DEVICE_NAME or (
                parsed_object.types[0] == SpiritCommon.data_model_type.MODEL_NAME and pnl.type == ".MODEL"):

            pnl.name = parsed_object.value

        elif pnl.type == ".DC":

            # .DC and .AC directives need four PARAM_NAME/PARAM_VALUE pairs - a sweep variable name,
            # a start value, a stop value, and a step value
            if not pnl.sweep_param_list:

                pnl.add_unused_sweep_params("dc")
                sweep_list = ["", "", "", ""]

                for sweep_item in sweep_list:

                    pnl.add_sweep_param_value(sweep_item)

            if parsed_object.types[0] == SpiritCommon.data_model_type.DC_SWEEP_DEV:
                
                pnl.add_unused_sweep_params("dev=" + parsed_object.value)

                # Only save if dc analysis does not involve a param
                if not pnl.sweep_param_list[0]:
                    pnl.sweep_param_list[0] = parsed_object.value
                    pnl.flag_unresolved_device = True

            elif parsed_object.types[0] == SpiritCommon.data_model_type.DC_SWEEP_PARAM:
                
                pnl.add_unused_sweep_params("param=" + parsed_object.value)

                if not parsed_object.value == "dc":

                    # Overwrite dc analysis with dev if it exists, reset unresolved
                    # device flag to False
                    pnl.sweep_param_list[0] = parsed_object.value
                    pnl.flag_unresolved_device = False

            elif parsed_object.types[0] == SpiritCommon.data_model_type.DC_SWEEP_START:
                
                pnl.sweep_param_list[1] = parsed_object.value

            elif parsed_object.types[0] == SpiritCommon.data_model_type.DC_SWEEP_STOP:
                
                pnl.sweep_param_list[2] = parsed_object.value

            elif parsed_object.types[0] == SpiritCommon.data_model_type.DC_SWEEP_STEP:
                
                pnl.sweep_param_list[3] = parsed_object.value

            elif parsed_object.types[0] == SpiritCommon.data_model_type.PARAM_NAME:
                
                sweep_param_name = parsed_object.value
                sweep_parsed_object = next(parsed_object_iter)

                if not sweep_parsed_object.types[0] == SpiritCommon.data_model_type.PARAM_VALUE:

                    logging.error(
                        "Line(s):" + str(pnl.linenum) + ". Parser passed wrong token.  Expected PARAM_VALUE.  Got " + str(
                            sweep_parsed_object.types[0]))
                    raise Exception("Next Token is not a PARAM_VALUE.  Something went wrong!")

                sweep_param_value = sweep_parsed_object.value
                pnl.add_unused_sweep_params(sweep_param_name + "=" + sweep_param_value)

        # For translation of port instance parameters to names recognized internally by XDM
        elif parsed_object.types[0] == SpiritCommon.data_model_type.PARAM_NAME and pnl.type == "P":

            param_value_parsed_object = next(parsed_object_iter)

            if parsed_object.value == "num":

                pnl.add_param_value_pair("PORT", param_value_parsed_object.value)
                
            elif parsed_object.value == "r":

                pnl.add_param_value_pair("Z0", param_value_parsed_object.value)
                
            elif parsed_object.value == "mag":

                pnl.add_param_value_pair("AC", param_value_parsed_object.value)
                
            elif parsed_object.value == "type":

                pass
                
            else:

                pnl.add_param_value_pair(parsed_object.value.upper(), param_value_parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.GENERALNODE and not pnl.type in [".IC", ".DCVOLT", ".NODESET"]:

            output_node = parsed_object.value

            if BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]] in pnl.known_objects and pnl.type == ".GLOBAL":

                pnl_synth = ParsedNetlistLine(pnl.filename, pnl.linenum)
                pnl_synth.type = ".GLOBAL"
                pnl_synth.local_type = ".GLOBAL"
                pnl_synth.add_known_object(output_node, BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]])
                synthesized_pnls.append(pnl_synth)

            else:

                pnl.add_known_object(output_node, BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]])

        elif parsed_object.types[0] == SpiritCommon.data_model_type.PARAM_NAME:

            # For Spectre, the polarity of the device (ex. NMOS or PMOS, or NPN or PNP) 
            # isn't declared as a separate identifier in the .MODEL statement. Instead, 
            # it is saved as a model parameter called "type". The polarity needs to be
            # extracted and saved in the data model consistent with SPICE parsing
            if pnl.type == ".MODEL" and parsed_object.value.upper() == "TYPE":

                param_value_parsed_object = next(parsed_object_iter)

                if pnl.known_objects.get(Types.modelType).endswith("MOS"):

                    pnl.add_known_object(param_value_parsed_object.value.upper()+"MOS", Types.modelType)

                elif pnl.known_objects.get(Types.modelType).endswith("JF"):

                    pnl.add_known_object(param_value_parsed_object.value.upper()+"JF", Types.modelType)

                else:

                    pnl.add_known_object(param_value_parsed_object.value, Types.modelType)

                pnl.add_param_value_pair(parsed_object.value, param_value_parsed_object.value)

            elif pnl.type == ".MODEL" and parsed_object.value.upper() == "VERSION":

                param_value_parsed_object = next(parsed_object_iter)
                pnl.add_param_value_pair(parsed_object.value.upper(), param_value_parsed_object.value)

            elif not parsed_object.value == "wave":

                param_value_parsed_object = next(parsed_object_iter)

                if pnl.type and pnl.type == ".TRAN":

                    self.set_tran_param(pnl, parsed_object.value, param_value_parsed_object.value)

                elif pnl.type and pnl.type == "V" or pnl.type == "I":

                    processed_value = param_value_parsed_object.value

                    # Some source paramters don't need curly braces, such as:
                    # The "type" parameter indicates source type, such as PULSE or PWL.
                    # The "file" parameter indicates the file to be opened.
                    if not parsed_object.value == "type" and not parsed_object.value == "file":

                        processed_value, msg = convert_to_xyce(processed_value)

                    processed_value = self.hack_ternary_operator(processed_value)
                    pnl.source_params[parsed_object.value] = processed_value

                else:

                    if param_value_parsed_object.types[0] != SpiritCommon.data_model_type.PARAM_VALUE:

                        raise Exception("Next Token is not a PARAM_VALUE.  Something went wrong!")

                    if (parsed_object.value.upper() == "M") and pnl.type not in ['R', 'L', 'C']:

                        pnl.m_param = param_value_parsed_object.value

                    msg = None
                    # expression = None
                    if param_value_parsed_object.value.startswith('[') and param_value_parsed_object.value.endswith(
                            ']'):

                        expression = param_value_parsed_object.value

                    elif is_a_number(param_value_parsed_object.value):

                        processed_value = param_value_parsed_object.value
                        expression = convert_si_unit_prefix(processed_value)

                    else:

                        # For parameters that refer to control devices, skip convert_to_xyce
                        # In the future, this will include cccs, etc.
                        processed_value, msg = convert_to_xyce(param_value_parsed_object.value)
                        expression = self.hack_ternary_operator(processed_value)

                    if expression:

                        pnl.add_param_value_pair(parsed_object.value, expression)

                    else:

                        pnl.add_param_value_pair(parsed_object.value, param_value_parsed_object.value)

                    if msg:

                        logging.warning("Error in expression: " + msg + str(parsed_object.value))

        elif parsed_object.types[0] == SpiritCommon.data_model_type.DC_VALUE_VALUE:

            processed_value, msg = convert_to_xyce(parsed_object.value)
            processed_value = self.hack_ternary_operator(processed_value)
            
            pnl.add_lazy_statement(processed_value, BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]])

        elif parsed_object.types[0] in [SpiritCommon.data_model_type.AC_MAG_VALUE, SpiritCommon.data_model_type.AC_PHASE_VALUE]:

            processed_value, msg = convert_to_xyce(parsed_object.value)
            processed_value = self.hack_ternary_operator(processed_value)

            if parsed_object.types[0] == SpiritCommon.data_model_type.AC_MAG_VALUE:
                pnl.add_known_object("AC", Types.acValue)
            
            pnl.add_known_object(processed_value, BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]])

        elif parsed_object.types[0] == SpiritCommon.data_model_type.CONTROL_DEVICE:

            control_dev_name_obj = next(parsed_object_iter)

            if control_dev_name_obj.types[0] != SpiritCommon.data_model_type.CONTROL_DEVICE_NAME:
                logging.error("Line(s):" + str(
                    pnl.linenum) + ". Parser passed wrong token.  Expected CONTROL_DEVICE_NAME.  Got " + str(
                    control_dev_name_obj.types[0]))
                raise Exception("Next Token is not a CONTROL_DEVICE_NAME.  Something went wrong!")

            pnl.add_control_param_value(control_dev_name_obj.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.OUTPUT_VARIABLE:

            formatted_output_variable = format_output_variable(parsed_object.value)
            pnl.add_output_variable_value(formatted_output_variable)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.UNKNOWN_NODE:

            pnl.add_unknown_node(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.COMMENT:

            # If a comment comes in the middle of a delimited block, synthesize a PNL
            # object for the comment and leave the original PNL unmolested
            if self._delimited_block:
                pnl_synth = ParsedNetlistLine(pnl.filename, [pnl.linenum[-1]])
                pnl_synth.type = "COMMENT"
                pnl_synth.name = parsed_object.value
                pnl_synth.add_comment(parsed_object.value)
                synthesized_pnls.append(pnl_synth)

            else:
                pnl.type = "COMMENT"
                pnl.name = parsed_object.value
                pnl.add_comment(parsed_object.value)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.LIB_ENTRY and pnl.type and not pnl.type == ".ENDL":

            # convert to .lib from .include
            pnl.type = ".LIB"
            pnl.add_known_object(parsed_object.value, BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]])

        elif parsed_object.types[0] == SpiritCommon.data_model_type.FUNC_EXPRESSION:

            processed_value, msg = convert_to_xyce(parsed_object.value)
            processed_value = self.hack_ternary_operator(processed_value)

            if not processed_value.startswith("{"):
                processed_value = "{" + processed_value + "}"

            pnl.add_known_object(processed_value, BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]])

        elif parsed_object.types[0] == SpiritCommon.data_model_type.CONDITIONAL_STATEMENT:

            comment = pnl.params_dict[Types.comment] + parsed_object.value
            pnl.add_comment(comment)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.BINNED_MODEL_NAME:

            # create a pnl for model binning option
            if not self._write_model_binning_option:

                pnl_synth = ParsedNetlistLine(pnl.filename, [0])  # what to do with line numbers?
                pnl_synth.type = ".OPTIONS"
                pnl_synth.local_type = ".OPTIONS"
                pnl_synth.add_known_object("PARSER", Types.optionPkgTypeValue)
                pnl_synth.add_param_value_pair("model_binning", "true")
                synthesized_pnls.append(pnl_synth)

                self._model_binning_option = True

            # if "." already in model name, need to create synthesized pnl for next
            # binned model
            if "." in pnl.name:

                model_name = pnl.name.split(".")[0]
                pnl_synth = ParsedNetlistLine(pnl.filename, [pnl.linenum[-1]])
                pnl_synth.type = ".MODEL"
                pnl_synth.local_type = "model"
                pnl_synth.name = model_name + "." + parsed_object.value
                pnl_synth.add_param_value_pair("LEVEL", pnl.params_dict["LEVEL"])
                pnl_synth.add_known_object(pnl.known_objects["MODEL_TYPE"], Types.modelType)
                synthesized_pnls.append(pnl_synth)
                self._modify_synth_pnl = True
                
            else:

                pnl.name = pnl.name + "." + parsed_object.value

        elif parsed_object.types[0] == SpiritCommon.data_model_type.VOLTAGE or parsed_object.types[0] == SpiritCommon.data_model_type.CURRENT:

            expression_obj = next(parsed_object_iter)

            if expression_obj.types[0] != SpiritCommon.data_model_type.EXPRESSION:

                logging.error("Line(s):" + str(
                    pnl.linenum) + ". Parser passed wrong token.  Expected EXPRESSION.  Got " + str(
                    expression_obj.types[0]))
                raise Exception("Next Token is not a EXPRESSION.  Something went wrong!")

            processed_value, msg = convert_to_xyce(expression_obj.value)
            processed_value = self.hack_ternary_operator(processed_value)
            pnl.add_known_object(processed_value, Types.expression)

            if parsed_object.types[0] == SpiritCommon.data_model_type.VOLTAGE:

                pnl.add_known_object(processed_value, Types.voltage)

            if parsed_object.types[0] == SpiritCommon.data_model_type.CURRENT:

                pnl.add_known_object(processed_value, Types.current)

        else:

            if is_a_number(parsed_object.value):

                parsed_object.value = convert_si_unit_prefix(parsed_object.value)

            XyceNetlistBoostParserInterface.convert_next_token(parsed_object, parsed_object_iter, pnl, synthesized_pnls)

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

    @property
    def tnom_defined(self):
        return self._tnom_defined

    @property
    def tnom_value(self):
        return self._tnom_value

    @property
    def temp_defined(self):
        return self._temp_defined
