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


class SWEEP(object):
    """
    A structure to represent the sweeps used in .AC, .DC,
    and .STEP.
    These sweeps are supported:

        * LIN (linear sweep, sweep variable is swept
          linearly from the starting to the ending value)
        * OCT (sweep by octaves, sweep variable is swept
          logarithmically by octaves)
        * DEC (sweep by decades, sweep variable is swept
          logarithmically by decades)
        * LIST (list of values, use a list of values)
        * DATA (steps through data in .DATA statement)

    Member variables:
        sweepType ("LIN", "DEC", "OCT", "LIST", "DATA")
        start
        stop
        step

    """
    def __init__(self):
        self._sweep_list = []

    @property
    def sweep_list(self):
        return self._sweep_list

    def add_sweep(self, sweep):
        self._sweep_list.append(sweep)

    def spice_string(self, delimiter=' '):
        return_string = ""
        for sweep in self._sweep_list:
            return_string += sweep.spice_string(delimiter)
            return_string += delimiter
        return return_string.strip()


class LIN_SWEEP(object):
    def __init__(self, sweep_variable_name, start, stop, step):
        self._sweep_variable_name = sweep_variable_name
        self._start = start
        self._stop = stop
        self._step = step

    @property
    def sweep_variable_name(self):
        return self._sweep_variable_name

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    @property
    def step(self):
        return self._step

    def spice_string(self, delimiter=' '):
        return_string = ""
        return_string += "LIN"
        return_string += delimiter
        return_string += self._sweep_variable_name
        return_string += delimiter
        return_string += self._start
        return_string += delimiter
        return_string += self._stop
        return_string += delimiter
        return_string += self._step
        return return_string.strip()


class DEC_SWEEP(object):
    def __init__(self, sweep_variable_name, start, stop, points):
        self._sweep_variable_name = sweep_variable_name
        self._start = start
        self._stop = stop
        self._points = points

    @property
    def sweep_variable_name(self):
        return self._sweep_variable_name

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    @property
    def step(self):
        return self._step

    @property
    def points(self):
        return self._points

    def spice_string(self, delimiter=' '):
        return_string = ""
        return_string += "DEC"
        return_string += delimiter
        return_string += self._sweep_variable_name
        return_string += delimiter
        return_string += self._start
        return_string += delimiter
        return_string += self._stop
        return_string += delimiter
        return_string += self._points
        return return_string.strip()


class OCT_SWEEP(object):
    def __init__(self, sweep_variable_name, start, stop, points):
        self._sweep_variable_name = sweep_variable_name
        self._start = start
        self._stop = stop
        self._points = points

    @property
    def sweep_variable_name(self):
        return self._sweep_variable_name

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    @property
    def step(self):
        return self._step

    @property
    def points(self):
        return self._points

    def spice_string(self, delimiter=' '):
        return_string = ""
        return_string += "OCT"
        return_string += delimiter
        return_string += self._sweep_variable_name
        return_string += delimiter
        return_string += self._start
        return_string += delimiter
        return_string += self._stop
        return_string += delimiter
        return_string += self._points
        return return_string.strip()


class LIST_SWEEP(object):
    def __init__(self, sweep_variable_name, value_list):
        self._sweep_variable_name = sweep_variable_name
        self._value_list = value_list

    @property
    def sweep_variable_name(self):
        return self._sweep_variable_name

    @property
    def value_list(self):
        return self._value_list

    def spice_string(self, delimiter=' '):
        return_string = ""
        return_string += self._sweep_variable_name
        return_string += delimiter
        return_string += "LIST"
        return_string += delimiter
        for item in self._value_list:
            return_string += item
            return_string += delimiter
        return return_string.strip()

class DATA_SWEEP(object):
    def __init__(self, sweep_variable_name):
        self._sweep_variable_name = sweep_variable_name

    @property
    def sweep_variable_name(self):
        return self._sweep_variable_name

    def spice_string(self, delimiter=' '):
        return_string = ""
        return_string += "DATA="
        return_string += self._sweep_variable_name
        return return_string.strip()
