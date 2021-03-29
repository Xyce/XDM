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


from xdm.statements import Statement
from xdm.index.GEN_STATEMENT_INDEX import GEN_STATEMENT_INDEX


class SRC_LINE_INDEX(GEN_STATEMENT_INDEX):
    """
    An index for enumerating source file/line in order.  This class extends
    GEN_STATEMENT_INDEX and sets the indexable object (SOURCE_FILE) attribute
    and the sorted order (by uid).

    """
    def __init__(self):
        GEN_STATEMENT_INDEX.__init__(self,
                                     lambda x: "" if x.file is None else x.file,
                                     lambda x: "" if x.line_num is None else x.line_num,
                                     Statement)
