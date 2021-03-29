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
from os.path import basename
from copy import deepcopy

from xdm.exceptions import InvalidParametersException
from xdm.exceptions import InvalidTypeException

transient_value_map = {"PULSE": ["I1", "I2", "TD", "TR", "TF", "PW", "PER"],
                       "SIN": ["I0", "IA", "FREQ", "TD", "THETA", "PHASE"],
                       "EXP": ["I1", "I2", "TD1", "TAU1", "TD2", "TAU2"],
                       "SFFM": ["IOFF", "IAMPL", "FC", "MOD", "FM"],
                       "PWL": []  # not used for PWL, see code below
                       }


class TRANSIENT(object):
    """
    A structure to represent the transient used in Independent
    Current Source and Independent Voltage Source.

    There are five predefined time-varying functions for sources:
        * PULSE(<parameters>) - pulse waveform
        * SIN(<parameters>) - sinusoidal waveform
        * EXP(<parameters>) - exponential waveform
        * PWL(<parameters>) - piecewise linear waveform
        * SFFM(<parameters>) - frequency-modulated waveform
    """

    def __init__(self, trans_type):
        if trans_type.upper() not in transient_value_map.keys():
            raise InvalidTypeException(trans_type + " is not a valid type of transient")
        self._transType = trans_type.upper()
        self._transParams = OrderedDict()

    @property
    def trans_type(self):
        return self._transType

    @property
    def trans_params(self):
        return self._transParams

    def set_transient_props(self, trans_list):
        param_used_count = 0

        # PWL plays by different rules - you can get pairs of values instead of expecting a
        # fixed number of values
        if self._transType == "PWL":
            # must come in pairs, creates list of pairs
            param_list = [(x,y) for x, y in zip(trans_list[::2], trans_list[1::2])]
            self._transParams = deepcopy(param_list)
        else:
            self._transParams = OrderedDict()

            values_to_fill = len(transient_value_map[self._transType])
            if len(trans_list) > values_to_fill:
                raise InvalidParametersException("Number of parameters in transient exceeds " +
                                                 "number of parameters in " + self._transType +
                                                 ". Expected: " + str(len(transient_value_map[self._transType])) +
                                                 ". Actual: " + str(len(trans_list)))
            for list_key in transient_value_map[self._transType]:
                if param_used_count < len(trans_list):
                    self._transParams[list_key] = trans_list[param_used_count]
                    param_used_count += 1
                else:
                    self._transParams[list_key] = None

    def spice_string(self, delimiter=' '):
        return_string = ''
        params_string = ''
        if self._transType == "PWL":
            file_bool = False

            for pair in self._transParams:
                if pair[0].upper() == "FILE":
                    file_bool = True

            for pair in self._transParams:
                params_string += pair[0]
                params_string += delimiter
                if file_bool:
                    params_string += '"' + pair[1] + '"'
                else:
                    params_string += pair[1]
                params_string += delimiter

            return_string += self._transType.strip()
            if file_bool:
                return_string += delimiter
            else:
                return_string += "("
            return_string += params_string.strip()
            if not file_bool:
                return_string += ")"

        else:
            for param in self._transParams:
                if self._transParams.get(param):
                    params_string += self._transParams.get(param, "") + delimiter

            return_string += self._transType.strip()
            return_string += "("
            return_string += params_string.strip()
            return_string += ")"

        return return_string

    @property
    def pwl_file(self):
        if self._transType == "PWL":
            found_file = None
            for i, trans_param in enumerate(self._transParams):
                if trans_param[0].upper() == "FILE":
                    found_file = (trans_param[1], i)
                    # trans_param = (trans_param[0], basename(trans_param[1]))
            if found_file:
                self._transParams[found_file[1]] = (
                    self._transParams[found_file[1]][0], basename(self._transParams[found_file[1]][1].replace('"', '')))
                return found_file[0]
        return None

    # The following code likely will be useful in the formulation of properties, but
    # we are moving away from having Params.  Commenting out until implementation of
    # props
# def param_types(self):
#         return transient_value_map[self._transType]
#
#     @params.setter
#     def params(self, params):
#         param_used_count = 0
#         values_to_fill = len(transient_value_map[self._transType])
#         if len(params) > values_to_fill:
#             raise InvalidParametersException("Number of parameters in transient exceeds " +
#                                                 "number of parameters in " + self._transType +
#                                                 ". Expected: " + str(len(transient_value_map[self._transType])) +
#                                                 ". Actual: " + str(len(params)))
#         for param_key in transient_value_map[self._transType]:
#             if param_used_count < len(params):
#                 self._transParams[param_key] = params[param_used_count]
#                 param_used_count += 1
#             else:
#                 self._transParams[param_key] = None
