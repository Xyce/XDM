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


# function to export context information for processing the C++ code.
def expr_spirit_interface(context):
    expr_parser = SpiritExprCommon.HSPICEExprBoostParser()

    expr_parser.py_dict = context.func_dict
    expr_parser.import_func_statements(expr_parser.py_dict)

    expr_parser.py_dict = context.func_arg_dict
    expr_parser.import_func_args(expr_parser.py_dict)

    expr_parser.py_list = context.param_list
    expr_parser.import_param_statements(expr_parser.py_list)

    return expr_parser


def trace_subckt_instantiations(top_hier, scope, global_scopes, sibling_scopes, context_list, inherited_scopes_to_include, is_top_level=False):
    import xdm.expr.Context as Context
    tot_st = len(scope.all_statements_in_scope)
    for key_ind, key in enumerate(scope.all_statements_in_scope):
        if "SUBCIRCUITNAME_VALUE" in scope.all_statements_in_scope[key].props:
            curr_hier = deepcopy(top_hier)
            curr_hier.append(("X" + scope.all_statements_in_scope[key].props["MY_NAME"], scope.all_statements_in_scope[key].props["SUBCIRCUITNAME_VALUE"].name))

            scopes_to_include = copy(inherited_scopes_to_include)
            # find if any other subckt definitions are contained within the same file as current
            # subckt. Always include top scope childrend (since it contains all includes) by adding
            # to sibling scope
            curr_sibling_scopes = []
            for child_scope in scope.children:
                if child_scope.subckt_command is not None:
                    curr_sibling_scopes.append(child_scope)

                    if is_top_level:
                        if child_scope not in global_scopes:
                            global_scopes.append(child_scope)

            curr_sibling_scopes.extend(global_scopes)

            # check if current subckt is using any other subckt definition within the same file
            sibling_scope_names = []
            for sibling_scope in sibling_scopes:
                sibling_scope_names.append(sibling_scope.subckt_command.name)
                if sibling_scope.subckt_command is not None:
                    if scope.all_statements_in_scope[key].props["SUBCIRCUITNAME_VALUE"].name == sibling_scope.subckt_command.name:
                        if sibling_scope not in scopes_to_include:
                            scopes_to_include.append(sibling_scope)
                        trace_subckt_instantiations(curr_hier, sibling_scope, global_scopes, curr_sibling_scopes, context_list, copy(scopes_to_include))

            if not scope.children:
                if key_ind < tot_st:
                    terminal_flag = True
                    if curr_hier:
                        for context in context_list:
                            if context.context_exists(curr_hier, scopes_to_include):
                                terminal_flag = False
                                break

                            if context.nonterminal_context(curr_hier):
                                terminal_flag = False
                                break

                        if terminal_flag:
                            curr_context = Context(curr_hier, copy(scopes_to_include))
                            context_list.append(curr_context)

                    curr_hier = ""

                    continue

                else:
                    return

            # check if current subckt is using any other subckt definition in another .inc file
            for child_scope in scope.children:
                if child_scope.subckt_command is not None:
                    # if subckt definition already checked, don't check again
                    if child_scope.subckt_command.name in sibling_scope_names:
                        continue

                    if scope.all_statements_in_scope[key].props["SUBCIRCUITNAME_VALUE"].name == child_scope.subckt_command.name:
                        if child_scope not in scopes_to_include:
                            scopes_to_include.append(child_scope)
                        trace_subckt_instantiations(curr_hier, child_scope, global_scopes, curr_sibling_scopes, context_list, copy(scopes_to_include))

            terminal_flag = True
            if curr_hier:
                for context in context_list:
                    if context.context_exists(curr_hier, scopes_to_include):
                        terminal_flag = False
                        break

                    if context.nonterminal_context(curr_hier):
                        terminal_flag = False
                        break

                if terminal_flag:
                    curr_context = Context(curr_hier, copy(scopes_to_include))
                    context_list.append(curr_context)

    return


def update_subckt_instantiations(top_hier, scope, global_scopes, sibling_scopes, scopes_to_include, hier_list, func_list, eval_list, subckt_update_info, is_top_level=False):
    # iterate through each of the scopes
    tot_st = len(scope.all_statements_in_scope)
    curr_hier = ""
    for key_ind, key in enumerate(scope.all_statements_in_scope):
        if is_top_level:
            curr_hier = ""
            scopes_to_include = []

        if "SUBCIRCUITNAME_VALUE" in scope.all_statements_in_scope[key].props:
            # record down the hierarchy
            if not top_hier:
                curr_hier = "X"+scope.all_statements_in_scope[key].props["MY_NAME"]
            else:
                curr_hier = top_hier + ":X"+scope.all_statements_in_scope[key].props["MY_NAME"]

            for ind, hier in enumerate(hier_list):
                # check if current hierarchy matches one that has an evaluation
                if curr_hier == hier.rsplit(":", 1)[0]:
                    subckt_name = scope.all_statements_in_scope[key].props["SUBCIRCUITNAME_VALUE"].name

                    # store info for subckt definition update step
                    if not subckt_name in subckt_update_info:
                        subckt_update_info[subckt_name] = {}
                        subckt_update_info[subckt_name]["FUNC_NAME"] = []
                        subckt_update_info[subckt_name]["PARAM_NAME"] = []
                        subckt_update_info[subckt_name]["FUNC_CALL"] = []

                    subckt_update_info[subckt_name]["FUNC_NAME"].append(func_list[ind].split("(")[0])
                    subckt_update_info[subckt_name]["PARAM_NAME"].append(hier.rsplit(":",1)[1])
                    subckt_update_info[subckt_name]["FUNC_CALL"].append(func_list[ind])

                    # add in new parameter for evaluated function
                    new_xyce_param_suffix = str(subckt_update_info[subckt_name]["FUNC_CALL"].index(func_list[ind]))
                    new_xyce_param = "XYCE_"+func_list[ind].split("(")[0].strip()+"_"+new_xyce_param_suffix
                    eval_result = eval_list[ind]
                    if eval_result == "nan":
                        eval_result = 0
                    scope.all_statements_in_scope[key].props["SUBCIRCUIT_PARAMS_LIST"][new_xyce_param] = str(eval_result)

            # find if any other subckt definitions are contained within the same file as current
            # subckt. Always include top scope childrend (since it contains all includes) by adding 
            # to sibling scope
            curr_sibling_scopes = []
            for child_scope in scope.children:
                if child_scope.subckt_command is not None:
                    curr_sibling_scopes.append(child_scope)

                    if is_top_level:
                        if child_scope not in global_scopes:
                            global_scopes.append(child_scope)

            if not is_top_level:
                curr_sibling_scopes.extend(global_scopes)

            # check if current subckt is using any other subckt definition within the same file
            sibling_scope_names = []
            for sibling_scope in sibling_scopes:
                sibling_scope_names.append(sibling_scope.subckt_command.name)
                if sibling_scope.subckt_command is not None:
                    if scope.all_statements_in_scope[key].props["SUBCIRCUITNAME_VALUE"].name == sibling_scope.subckt_command.name:
                        if sibling_scope not in scopes_to_include:
                            scopes_to_include.append(sibling_scope)
                        update_subckt_instantiations(curr_hier, sibling_scope, global_scopes, curr_sibling_scopes, scopes_to_include, hier_list, func_list, eval_list, subckt_update_info)

            if not scope.children:
                if key_ind < tot_st:
                    curr_hier = ""

                    continue
                return

            # check if current subckt is using any other subckt definition in another .inc file
            for child_scope in scope.children:
                if child_scope.subckt_command is not None:
                    # if subckt definition already checked, don't check again
                    if child_scope.subckt_command.name in sibling_scope_names:
                        continue

                    if scope.all_statements_in_scope[key].props["SUBCIRCUITNAME_VALUE"].name == child_scope.subckt_command.name:
                        if child_scope not in scopes_to_include:
                            scopes_to_include.append(child_scope)
                        update_subckt_instantiations(curr_hier, child_scope, global_scopes, curr_sibling_scopes, scopes_to_include, hier_list, func_list, eval_list, subckt_update_info)

    return


def update_subckt(subckts_to_update, subckt_update_info):
    for subckt_scope_dict in subckts_to_update:
        if subckt_scope_dict.subckt_command.name in subckt_update_info:
            for ind, func_name in enumerate(subckt_update_info[subckt_scope_dict.subckt_command.name]["FUNC_NAME"]):
                # first update the subckt declaration line
                new_xyce_param = "XYCE_" + func_name + "_" + str(ind)
                subckt_scope_dict.subckt_command.props["SUBCIRCUIT_PARAMS_LIST"][new_xyce_param] = "0"

                curr_func_call = subckt_update_info[subckt_scope_dict.subckt_command.name]["FUNC_CALL"][ind]
                curr_param_name = subckt_update_info[subckt_scope_dict.subckt_command.name]["PARAM_NAME"][ind]

                # next update parameter statements where the function call appears in
                for key in subckt_scope_dict.all_statements_in_scope:
                    i = subckt_scope_dict.all_statements_in_scope[key]
                    if "PARAMS_LIST" in i.props:
                        if curr_param_name in i.props["PARAMS_LIST"]:
                            expr = i.props["PARAMS_LIST"][curr_param_name].upper().replace(" ", "")
                            expr = expr.replace(curr_func_call, new_xyce_param)
                            expr = ternary_clean_up(expr)
                            i.props["PARAMS_LIST"][curr_param_name] = expr

    return


def update_params(full_hier, param_names, func_calls, eval_result, st_to_process, scope_names):
    # get hierarchy
    full_hier_prefix = ""
    curr_subckt = ""
    if full_hier:
        hiers = full_hier.split(")")

        for hier in hiers:
            devname, subckt = hier.split("(")
            full_hier_prefix += devname + ":"
            curr_subckt = subckt

    # find param statements
    for ind, scope_dict in enumerate(st_to_process):
        if scope_names[ind] != curr_subckt:
            continue

        for key in scope_dict:
            i = scope_dict[key]

            if i.props[Types.statementType] == "__COMMAND__":
                if i.command_type == ".PARAM":
                    for curr_param_name in i.props["PARAMS_LIST"]:
                        curr_hier_param_name = full_hier_prefix + curr_param_name

                        if curr_hier_param_name in param_names:
                            curr_ind = param_names.index(curr_hier_param_name)
                            curr_func_call = func_calls[curr_ind].replace(" ", "")
                            curr_result = eval_result[curr_ind]
                            if str(curr_result) == "nan":
                                curr_result = 0

                            expr = i.props["PARAMS_LIST"][curr_param_name].upper().replace(" ", "")
                            expr = expr.replace(curr_func_call, str(curr_result))
                            expr = ternary_clean_up(expr)
                            i.props["PARAMS_LIST"][curr_param_name] = expr

    return


# This is a copy of the hack_ternary_operator method in HSPICENetlistBoostParserInterface.
# It's needed to put back in a space before the ":" in ternary operators, since spaces need
# to be eliminated for replacement of functions with their evaluated result
def ternary_clean_up(in_expression):
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
                    return in_expression
                else:
                    q_list.pop()

                    # if there's an empty space to the left of ":", no need to add another
                    if out_expression[-1] == " ":
                        out_expression += char
                    else:
                        out_expression += " " + char
            else:
                out_expression += char

        if q_list:
            return in_expression

    # if no ternary operator in expression, return expression unchanged
    else:
        return in_expression

    return out_expression


def comment_out_funcs(sli):
    for fl, objs in sli:
        objs_to_delete = []
        comments_to_add = []
        # find all .FUNC in each file. add key to list of keys to be deleted. create
        # corresponding comment data model object
        for obj in objs:
            if isinstance(obj, Command):
                if obj.command_type == ".FUNC":
                    objs_to_delete.append(obj)

                    func_name = obj.props["FUNC_NAME_VALUE"].upper()
                    func_args = "(" + ",".join([x.upper() for x in obj.props["FUNC_ARG_LIST"]]) + ")"
                    func_expr = obj.props["FUNC_EXPRESSION"].upper()
                    props = {}
                    props[Types.name] = ".FUNC " + func_name + func_args + " " + func_expr
                    props[Types.statementType] = "__REF__"
                    props["COMMENT"] = ".FUNC " + func_name + func_args + " " + func_expr
                    comment = COMMENT(props, obj.file, obj.line_num, obj.uid)
                    comments_to_add.append(comment)

        # replace .FUNC command data model objects with the comment data model objects
        for obj, comment in zip(objs_to_delete, comments_to_add):
            ind = sli.statement_dict[fl].index(obj)
            sli.statement_dict[fl][ind] = comment

    return
