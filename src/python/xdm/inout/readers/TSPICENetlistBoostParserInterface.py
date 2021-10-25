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
import xdm.Types as Types

import SpiritCommon

from xdm.inout.readers.XyceNetlistBoostParserInterface import XyceNetlistBoostParserInterface
from xdm.inout.readers.ParsedNetlistLine import ParsedNetlistLine

tspice_to_adm_model_type_map = {}
tspice_to_adm_opt_name_map = {}


class TSPICENetlistBoostParserInterface(object):
    """
    Allows for TSPICE to be read in using the Boost Parser.  Iterates over
    statements within the TSPICE netlist file.
    """
    def __init__(self, filename, language_definition, top_level_file=True):
        self.internal_parser = SpiritCommon.TSPICENetlistBoostParser()
        goodfile = self.internal_parser.open(filename, top_level_file)
        self.line_iter = iter(self.internal_parser)
        self._filename = filename
        self._language_definition = language_definition
        self._top_level_file = top_level_file
        self._tnom_defined = False
        self._temp_defined = False
        self._tnom_value = "27"

        self._pkg_dict = {}

        for package_type, prop_type_list in self._language_definition.get_directive_by_name(".OPTIONS").nested_prop_dict.items():
            for prop_type in prop_type_list:
                if prop_type.label.upper() in self._pkg_dict.keys():
                    self._pkg_dict[prop_type.label.upper()].append(package_type)
                else:
                    self._pkg_dict[prop_type.label.upper()] = [package_type]

        if not goodfile:
            logging.error("File: " + filename + " is not found!")
            raise Exception("File: " + filename + " is not found!")

        # a list of parsed netlist line objects created during
        # conversion to adm.
        self._synthesized_pnls = []

    def __del__(self):
        self.internal_parser.close()

    def __iter__(self):
        return self

    def __next__(self):

        # if there are synthesized objects, return these before continuing with file parse
        if len(self._synthesized_pnls) > 0:
            return self._synthesized_pnls.pop()

        boost_parsed_line = next(self.line_iter)

        pnl = ParsedNetlistLine(boost_parsed_line.filename, boost_parsed_line.linenums)

        parsed_object_iter = iter(boost_parsed_line.parsed_objects)

        for parsedObject in parsed_object_iter:
            self.convert_next_token(parsedObject, parsed_object_iter, pnl, self._synthesized_pnls, self._pkg_dict)

        if boost_parsed_line.error_type == "critical":
            pnl.error_type = boost_parsed_line.error_type
            pnl.error_message = boost_parsed_line.error_message
            logging.critical("In file:\"" + pnl.filename + "\" at line:" + str(pnl.linenum) + ". " + boost_parsed_line.error_message)
        elif boost_parsed_line.error_type == "error":
            pnl.error_type = boost_parsed_line.error_type
            pnl.error_message = boost_parsed_line.error_message
            logging.error("In file:\"" + pnl.filename + "\" at line:" + str(pnl.linenum) + ". " + boost_parsed_line.error_message)
        elif boost_parsed_line.error_type == "warn":
            pnl.error_type = boost_parsed_line.error_type
            pnl.error_message = boost_parsed_line.error_message
            logging.warn("In file:\"" + pnl.filename + "\" at line:" + str(pnl.linenum) + ". " + boost_parsed_line.error_message)
        elif boost_parsed_line.error_type == "info":
            pnl.error_type = boost_parsed_line.error_type
            pnl.error_message = boost_parsed_line.error_message
            logging.info("In file:\"" + pnl.filename + "\" at line:" + str(pnl.linenum) + ". " + boost_parsed_line.error_message)
        else:
            pnl.error_type = " "

        return pnl

    @staticmethod
    def convert_next_token(parsed_object, parsed_object_iter, pnl, synthesized_pnls, pkg_dict):

        if parsed_object.types[0] == SpiritCommon.data_model_type.PARAM_NAME and pnl.type == ".OPTIONS":

            # find the adm option name
            mapped_name = tspice_to_adm_opt_name_map.get(parsed_object.value.upper(), parsed_object.value.upper())

            # find all adm packages that use this parameter
            pkgs = pkg_dict.get(mapped_name.upper())

            if pkgs:
                param_value_parsed_object = next(parsed_object_iter)

                if param_value_parsed_object.types[0] != SpiritCommon.data_model_type.PARAM_VALUE:
                    logging.error("In file:\"" + pnl.filename + "\" at line:" + str(pnl.linenum) + ". Parser passed wrong token.  Expected PARAM_VALUE.  Got " + str(param_value_parsed_object.types[0]))
                    raise Exception("Next Token is not a PARAM_VALUE.  Something went wrong!")

                pnl.add_known_object(pkgs[0], Types.optionPkgTypeValue)

                param_value = param_value_parsed_object.value

                # converting .OPTIONS METHOD=DEFAULT to .OPTIONS TIMEINT METHOD=TRAP
                if mapped_name.upper() == "METHOD" and param_value.upper() == "DEFAULT":
                    param_value = "TRAP"

                pnl.add_param_value_pair(mapped_name.upper(), param_value)

                for otherPkg in pkgs[1:]:
                    pnl_synth = ParsedNetlistLine(pnl.filename, pnl.linenum)  # what to do with line numbers?
                    pnl_synth.type = ".OPTIONS"
                    pnl_synth.add_known_object(otherPkg, Types.optionPkgTypeValue)
                    pnl_synth.add_param_value_pair(mapped_name.upper(), param_value)
                    synthesized_pnls.append(pnl_synth)
            else:
                logging.warn("In file:\"" + pnl.filename + "\" at line:" + str(pnl.linenum) + ". Could not accept .OPTIONS \"" + mapped_name.upper() + "\". Retained (as a comment). Continuing.")
                pnl.type = "COMMENT"
                pnl.name = ".OPTIONS " + mapped_name
                pnl.add_comment(".OPTIONS " + mapped_name)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME and parsed_object.value.upper() == ".LIB":
            pnl.type = ".INC"

        elif parsed_object.types[0] == SpiritCommon.data_model_type.DIRECTIVE_NAME and parsed_object.value == ".PARAM":
            pnl.type = ".GLOBAL_PARAM"

        elif parsed_object.types[0] == SpiritCommon.data_model_type.OUTPUT_VARIABLE:

            # remove [] from PSPICE print variables -- eventually this will be replaced in the writer
            output_variable_clean = parsed_object.value
            output_variable_clean = output_variable_clean.replace("[", "")
            output_variable_clean = output_variable_clean.replace("]", "")
            output_variable_clean = output_variable_clean.replace("N(", "V(")
            output_variable_clean = output_variable_clean.replace("N(", "V(")

            pnl.add_output_variable_value(output_variable_clean)

        elif parsed_object.types[0] == SpiritCommon.data_model_type.MODEL_TYPE and pnl.type == ".MODEL":

            # convert pspice type into the general type supported by the ADM
            adm_type = tspice_to_adm_model_type_map.get(parsed_object.value.upper())

            # if not mapped, then use current value
            if adm_type is None:
                adm_type = parsed_object.value.upper()

            pnl.add_known_object(adm_type, Types.modelType)
        else:
            XyceNetlistBoostParserInterface.convert_next_token(parsed_object, parsed_object_iter, pnl, synthesized_pnls)

    @property
    def tnom_defined(self):
        return self._tnom_defined

    @property
    def tnom_value(self):
        return self._tnom_value

    @property
    def temp_defined(self):
        return self._temp_defined
