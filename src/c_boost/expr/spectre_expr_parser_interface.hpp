//-------------------------------------------------------------------------
//   Copyright 2002-2020 National Technology & Engineering Solutions of
//   Sandia, LLC (NTESS).  Under the terms of Contract DE-NA0003525 with
//   NTESS, the U.S. Government retains certain rights in this software.
//
//   This file is part of the Xyce(TM) XDM Netlist Translator.
//   
//   Xyce(TM) XDM is free software: you can redistribute it and/or modify
//   it under the terms of the GNU General Public License as published by
//   the Free Software Foundation, either version 3 of the License, or
//   (at your option) any later version.
//  
//   Xyce(TM) XDM is distributed in the hope that it will be useful,
//   but WITHOUT ANY WARRANTY; without even the implied warranty of
//   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//   GNU General Public License for more details.
//   
//   You should have received a copy of the GNU General Public License
//   along with the Xyce(TM) XDM Netlist Translator.
//   If not, see <http://www.gnu.org/licenses/>.
//-------------------------------------------------------------------------


#ifndef SPECTRE_EXPR_PARSER_INTERFACE_HPP
#define SPECTRE_EXPR_PARSER_INTERFACE_HPP


#include "ast_common.hpp"
#include "boost_expr_parser_common.h"
#include "expr_parser_interface.hpp"

#include <boost/algorithm/string.hpp>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/map_indexing_suite.hpp>

#include <map>
#include <queue>
#include <string>
#include <unordered_map>
#include <vector>


class SpectreExprBoostParser
{
    public:
        boost::python::dict dict;
        boost::python::list list;
        boost::python::list list2;
        std::vector<std::string> param_list;
        std::unordered_map<std::string, double> variable_map;
        std::unordered_map<std::string, std::string> function_map;
        std::unordered_map<std::string, std::map<int, std::string>> function_variable_map;

        BoostParsedExpr parseExpr(std::string pythonExpr);
        void import_func_statements(boost::python::dict & py_dict);
        void import_func_args(boost::python::dict & py_dict);
        void import_param_statements(boost::python::list & py_list);
        BoostEvaluatedExpr eval_statements(boost::python::list & py_list,
                                           boost::python::list & py_list_2);
        void print_maps();

};


#endif
