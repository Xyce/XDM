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

from copy import copy, deepcopy

from xdm import Types
from xdm.statements.commands import Command
from xdm.statements.refs import COMMENT
#import xdm.expr.Context as Context

import SpiritExprCommon


# function to find certain lexical tokens (defined in the search_expr_list) in an
# expression (in_expr). The expression elements are saved into an output
# list (found_list). If search_expr_list is empty, the function returns all
# lexical tokens found
def find_expr_components(in_expr, search_expr_list, found_list, debug=False, lang="hspice"):
    if lang == "spectre":
        expr_parser = SpiritExprCommon.SpectreExprBoostParser()
    else:
        expr_parser = SpiritExprCommon.HSPICEExprBoostParser()
    parsed_expr = expr_parser.parseExpr(in_expr)

    if not parsed_expr.error_type:
        for parsed_expr_object in parsed_expr.parsed_expr_objects:
            if search_expr_list:
                if parsed_expr_object.types[0] in search_expr_list:
                    found_list.append(parsed_expr_object)

            else:
                found_list.append(parsed_expr_object)

            if debug:
                if parsed_expr_object.types[0] == SpiritExprCommon.expr_data_model_type.FUNC_NAME:
                    print(parsed_expr_object.value, "FUNC_NAME")
                elif parsed_expr_object.types[0] == SpiritExprCommon.expr_data_model_type.PARAM_NAME:
                    print(parsed_expr_object.value, "PARAM_NAME")
                elif parsed_expr_object.types[0] == SpiritExprCommon.expr_data_model_type.NUMBER:
                    print(parsed_expr_object.value, "NUMBER")
    return
