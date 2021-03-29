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


class AC(object):
    """
        AC Value special class

        Form: [AC [magnitude value [phase value] ] ]
    """

    def __init__(self, mag_value, phase_value):
        self._mag_value = mag_value
        self._phase_value = phase_value

    @property
    def mag_value(self):
        return self._mag_value

    @property
    def phase_value(self):
        return self._phase_value

    def spice_string(self, delimiter=' '):
        return_string = ''
        return_string += 'AC'

        if self._mag_value:
            return_string += delimiter
            return_string += self._mag_value

            if self._phase_value:
                return_string += delimiter
                return_string += self._phase_value

        return return_string
