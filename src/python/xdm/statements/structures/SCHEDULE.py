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


class SCHEDULE(object):
    """
    A structure to represent the schedule used in .TRAN.
    It specifies a schedule for maximum allowed time steps.
    They come in the form:

    [{schedule( <time>, <maximum time step>, ... )}]

    The list of arguments, t0, <delta>t0, t1, <delta>t1, etc.
    implies that a maximum time step of <delta>t0 will be
    used while the simulation time is greater than or equal
    tot0 and less than t1.  A maximum time step of <delta>t1
    will be used when the simulation time is greater or
    equal to t1 and less than t2.

    This sequence will continue for all pairs of ti, <delta>ti
    that are given in the {schedule()}.  If <delta>t is zero
    or negative, then no maximum time step is enforced
    (other than hardware limits of the host computer).

    """

    def __init__(self):
        self._time_max_step_pairs = []  # python type list

    @property
    def time_max_step_pairs(self):
        return self._time_max_step_pairs

    def add_time_max_step_pair(self, time, max_time_step):
        self._time_max_step_pairs.append((time, max_time_step))

    def spice_string(self, delimiter=' '):
        return_string = ""
        if len(self._time_max_step_pairs) > 0:
            return_string += '{'
            return_string += 'schedule('
            for pair in self._time_max_step_pairs:
                return_string += pair[0]
                return_string += ','
                return_string += delimiter
                return_string += pair[1]
                return_string += ','
                return_string += delimiter
            return_string = return_string[:-2]  # removes last comma and delimiter
            return_string += ')}'

        return return_string
