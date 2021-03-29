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
import sys

import SpiritCommon

from xdm import Types
from xdm.inout.readers import BoostParserInterface
from xdm.inout.readers.ParsedNetlistLine import ParsedNetlistLine
from xdm.inout.readers.XyceNetlistBoostParserInterface import XyceNetlistBoostParserInterface


# maps pspice model types into their ADM (xyce style) model types
pspice_to_adm_model_type_map = {"RES": "R",
                                "IND": "L",
                                "CORE": "CORE",
                                "D": "D",
                                "CAP": "C",
                                "PNP": "PNP",
                                "NPN": "NPN",
                                "LPNP": "LPNP",  # assuming it is the same - q device
                                "NIGBT": "NMF",  # is this right?
                                "NMOS": "NMOS",
                                "PMOS": "PMOS",
                                "DOUTPUT": "LTRA",  # is this right?
                                "VSWITCH": "VSWITCH",
                                "ISWITCH": "ISWITCH",
                                "UADC": "DIG",  # U devices?
                                "UDAC": "DIG",
                                "UDLY": "DIG",
                                "UEFF": "DIG",
                                "UGATE": "DIG",
                                "UGFF": "DIG",
                                "UIO": "DIG",
                                "UTGATE": "DIG",
                                "NJF": "NJF",
                                "PJF": "PJF",
                                "GASFET": "B",  # does not exist in reference manual
                                "DINPUT": "N",  # N device does not exist in Xyce
                                "TRN": "LTRA"  # is this right? O device in Xyce is T device in PSPICE?
                                }

default_values = {
    "ITL1": "200",
    "ITL4": "20"
}


class PSPICENetlistBoostParserInterface(object):
    """
    Allows for PSPICE to be read in using the Boost Parser.  Iterates over
    statements within the PSPICE netlist fiAle.
    """
    def __init__(self, filename, language_definition, top_level_file=True):
        self.internal_parser = SpiritCommon.PSPICENetlistBoostParser()
        self.goodfile = self.internal_parser.open(filename, top_level_file)
        self.line_iter = iter(self.internal_parser)
        self._filename = filename
        self._language_definition = language_definition
        self._top_level_file = top_level_file

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

        if (parsed_object.types[0] == SpiritCommon.data_model_type.PARAM_NAME or parsed_object.types[0] == SpiritCommon.data_model_type.DEFAULT_PARAM_NAME) and pnl.type == ".OPTIONS":

            # find the adm option name
            orig_param_name = parsed_object.value.upper()
            param_name = orig_param_name

            # find all adm packages that use this parameter
            pkgs = pkg_dict.get(param_name.upper())

            # TODO: Hack Bugzilla 2020, ITL1 => NONLIN MAXSTEP (default 200)
            # TODO: Hack Bugzilla 2020, ITL4 => NONLIN-TRAN MAXSTEP (default 20)

            # TODO: Hack Bugzilla 2020, VNTOL => ABSTOL

            param_name, pkgs = self.hack_packages_bugzilla_2020(param_name.upper(), pkgs)

            if pkgs:
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

                for otherPkg in pkgs[1:]:
                    pnl_synth = ParsedNetlistLine(pnl.filename, pnl.linenum)  # what to do with line numbers?
                    pnl_synth.type = ".OPTIONS"
                    pnl_synth.add_known_object(otherPkg, Types.optionPkgTypeValue)
                    pnl_synth.add_param_value_pair(param_name.upper(), param_value)
                    synthesized_pnls.append(pnl_synth)

            else:
                logging.warning("In file:\"" + str(os.path.basename(pnl.filename)) + "\" at line:" + str(pnl.linenum) + ". Could not accept .OPTIONS \"" + orig_param_name.upper() + "\". Retained (as a comment). Continuing.")
                pnl.type = "COMMENT"
                pnl.name = ".OPTIONS " + orig_param_name
                pnl.add_comment(".OPTIONS " + orig_param_name)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME and parsed_object.value.upper() == ".LIB":
            pnl.type = ".INC"

        elif parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME and parsed_object.value == ".PARAM":
            pnl.type = ".GLOBAL_PARAM"

        elif parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME and (parsed_object.value.upper() == ".PROBE" or parsed_object.value.upper() == ".PROBE64"):
            pnl.type = ".PRINT"
            pnl.add_known_object("TRAN", Types.analysisTypeValue)  # default tran type

        elif parsed_object.types[0] == SpiritCommon.data_model_type.OUTPUT_VARIABLE:

            # remove [] from PSPICE print variables -- eventually this will be replaced in the writer
            output_variable_clean = self.clean_pspice_output_variable(parsed_object.value)

            pnl.add_output_variable_value(output_variable_clean)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.MODEL_TYPE and pnl.type == ".MODEL":

            # convert pspice type into the general type supported by the ADM
            adm_type = pspice_to_adm_model_type_map.get(parsed_object.value.upper())

            # if not mapped, then use current value
            if not adm_type:
                adm_type = parsed_object.value.upper()

            pnl.add_known_object(adm_type, Types.modelType)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.GENERALNODE and not pnl.type in [".IC", ".DCVOLT", ".NODESET"]:
            output_node = parsed_object.value.replace(".", ":")
            pnl.add_known_object(output_node, BoostParserInterface.boost_xdm_map_dict[parsed_object.types[0]])

        else:
            XyceNetlistBoostParserInterface.convert_next_token(parsed_object, parsed_object_iter, pnl, synthesized_pnls)

    @staticmethod
    def clean_pspice_output_variable(in_output_variable):
        """
        In Output Variables, removes brackets, converts N to V, and IA/IB to I1/I2
        """

        out_output_variable = in_output_variable.replace("[", "")
        out_output_variable = out_output_variable.replace("]", "")
        out_output_variable = out_output_variable.replace("N(", "V(")
        out_output_variable = out_output_variable.replace("IA(", "I1(")
        out_output_variable = out_output_variable.replace("IB(", "I2(")

        # replace "." with ":" when it is not an expression
        if "{" not in out_output_variable:
            out_output_variable = out_output_variable.replace(".", ":")

        return out_output_variable

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
        elif param == "ABSTOL":  # PSPICE ABSTOL is not Xyce ABSTOL
            logging.info("Removing ABSTOL.  PSPice ABSTOL is not the equivalent of Xyce ABSTOL")
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
