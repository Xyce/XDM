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
from collections import OrderedDict
from os.path import basename

from xdm.exceptions import InvalidParametersException
from xdm.exceptions import InvalidTypeException

measure_value_map = {"AC": ["AT", "AVG", "PARAM", "EQN", "FIND", "MAX", "MIN", "PP",
                            "WHEN"],
                     "DC": ["AT", "AVG", "PARAM", "EQN", "ERROR", "FIND", "MAX", "MIN", 
                            "PP", "WHEN"],
                     "TRAN": ["AT", "AVG", "DERIV", "DUTY", "EQN", "ERROR", "FIND", 
                              "FOUR", "FREQ", "INTEG", "MAX", "MIN", "OFF_TIME",
                              "ON_TIME", "PP", "RMS", "WHEN", "TRIG", "TARG"],
                       }


class MEASURE(object):
    """
    A structure to represent the measurement parameters, types, and qualifiers in 
    the measurement statement. Currently a WIP.

    There are three analysis types that work with measure statements:
        * DC
        * AC
        * TRAN

    There are sixteen different types of measurements that can be performed:
        * AVG(<parameters>)
        * DERIV(<parameters>) 
        * DUTY(<parameters>) 
        * ERROR(<parameters>) 
        * EQN(<parameters>)
        * FIND(<parameters>)
        * FOUR(<parameters>)
        * INTEG(<parameters>)
        * MAX(<parameters>)
        * MIN(<parameters>)
        * OFF_TIME(<parameters>)
        * ON_TIME(<parameters>)
        * PARAM(<parameters>)
        * PP(<parameters>)
        * RMS(<parameters>)
        * TRIG(<parameters>)

    Some of these measurement types can have qualifiers to them:
        * AT(<parameters>)
        * FILE(<parameters>) 
        * TARG(<parameters>) 
        * WHEN(<parameters>) 
    """

    def __init__(self, analysis_type, pnl):
        self._comment = False
        if analysis_type.upper() not in measure_value_map.keys():
            logging.warning("In file:\"" + str(basename(pnl.filename))
                            + "\" at Line(s):" + str(pnl.linenum) + "."
                            + analysis_type + " is not a valid analysis for measurement statement.")
            self._comment = True
        self._analysisType = analysis_type.upper()
        self._measureType = ""
        self._measureTypeParams = OrderedDict()
        self._measureQualifier = ""
        self._measureQualifierParams = OrderedDict()

    @property
    def comment(self):
        return self._comment

    @property
    def analysis_type(self):
        return self._analysisType

    @property
    def measure_type(self):
        return self._measureType

    @property
    def measure_type_params(self):
        return self._measureTypeParams

    @property
    def measure_qualifier(self):
        return self._measureQualifier

    @property
    def measure_qualifier_params(self):
        return self._measureQualifierParams

    def set_measure_type(self, pnl, language_directive_type):
        meas_dict = pnl.meas_dict
        params_dict = pnl.params_dict

        for curr_key, curr_dict in list(meas_dict.items()):
            self._measureType = curr_key.upper()
            measure_type_dict = curr_dict

            break

        if self._measureType.upper() not in measure_value_map[self._analysisType]:
            logging.warning("In file:\"" + str(basename(pnl.filename))
                            + "\" at Line(s):" + str(pnl.linenum) + ". "
                            + self._measureType.upper() + " is not a valid measure type for analysis " + self._analysisType + ".")
            self._comment = True

        for ind, (meas_param_name, meas_param_value) in enumerate(list(measure_type_dict.items())):
            if ind == 0:
                # self._measureTypeParams[meas_param_name] = meas_param_value
                if "VAL" in measure_type_dict:
                    self._measureTypeParams[meas_param_name] = measure_type_dict["VAL"]
                else:
                    self._measureTypeParams[meas_param_name] = meas_param_value

                continue

            for prop in language_directive_type.nested_prop_dict[self._measureType]:
                if prop.label.upper() == meas_param_name.upper():
                    self._measureTypeParams[meas_param_name] = meas_param_value

            if meas_param_name not in self._measureTypeParams:
                params_dict[meas_param_name] = meas_param_value

        return

    def set_measure_qualifier(self, pnl, language_directive_type):
        meas_dict = pnl.meas_dict
        params_dict = pnl.params_dict

        for curr_ind, (curr_key, curr_dict) in enumerate(list(meas_dict.items())):
            self._measureQualifier = curr_key.upper()
            measure_type_dict = curr_dict
            ind = curr_ind

        if ind == 0:
            self._measureQualifier = ""

            return

        if self._measureQualifier.upper() not in measure_value_map[self._analysisType]:
            logging.warning("In file:\"" + str(basename(pnl.filename))
                            + "\" at Line(s):" + str(pnl.linenum) + ". "
                            + self._measureQualifier.upper() + " is not a valid measure type for analysis " + self._analysisType + ".")
            self._comment = True

        for ind, (meas_param_name, meas_param_value) in enumerate(list(measure_type_dict.items())):
            if ind == 0:
                # self._measureTypeParams[meas_param_name] = meas_param_value
                if "VAL" in measure_type_dict:
                    self._measureQualifierParams[meas_param_name] = measure_type_dict["VAL"]
                else:
                    self._measureQualifierParams[meas_param_name] = meas_param_value

                continue

            for prop in language_directive_type.nested_prop_dict[self._measureQualifier]:
                if prop.label.upper() == meas_param_name.upper():
                    self._measureQualifierParams[meas_param_name] = meas_param_value

            if meas_param_name not in self._measureQualifierParams:
                params_dict[meas_param_name] = meas_param_value

        return

    def spice_string(self, delimiter=' '):
        return_string = ''

        if self._measureType:
            return_string += self._measureType.upper()

            for param, value in self._measureTypeParams.items():
                if value:
                    return_string += ' ' + param + '=' + value
                else:
                    return_string += ' ' + param

        if self._measureQualifier:
            return_string += ' ' + self._measureQualifier.upper()

            for param, value in self._measureQualifierParams.items():
                if value:
                    return_string += ' ' + param + '=' + value
                else:
                    return_string += ' ' + param

        return return_string
