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


#include "expr_parser_interface.hpp"
#include "hspice_expr_parser_interface.hpp"
#include "spectre_expr_parser_interface.hpp"
#include <boost/algorithm/string.hpp>
#include <fstream>
#include <iostream>

void convert_to_parsed_objects(std::vector<expr_boost_common::expr_object> expr_parse_results, BoostParsedExpr parsedExpr) 
{

    for(int i = 0; i < expr_parse_results.size(); i++) 
    {

        boost::python::list typeList;

        for(int j = 0; j < expr_parse_results[i].candidate_types.size(); j++) 
        {
            typeList.append(expr_parse_results[i].candidate_types[j]);
        }

        ParseExprObject obj;
        obj.value = expr_parse_results[i].value;
        obj.types = typeList;

        parsedExpr.parsedExprObjects.append(obj);
    }
}

BOOST_PYTHON_MODULE(SpiritExprCommon)
{
    boost::python::class_<ParseExprObject>("ParseExprObject")
        .def_readonly("value", &ParseExprObject::value)
        .def_readonly("types", &ParseExprObject::types)
        ;

    boost::python::class_<BoostParsedExpr>("BoostParsedExpr")
        .def_readonly("parsed_expr_objects", &BoostParsedExpr::parsedExprObjects)
        .def_readonly("sourceline", &BoostParsedExpr::sourceLine)
        .def_readonly("error_type", &BoostParsedExpr::errorType)
        .def_readonly("error_message", &BoostParsedExpr::errorMessage)
        ;

    boost::python::class_<BoostEvaluatedExpr>("BoostEvaluatedExpr")
        .def_readonly("evalResult", &BoostEvaluatedExpr::evalResult)
        .def_readonly("error_type", &BoostEvaluatedExpr::errorType)
        .def_readonly("error_message", &BoostEvaluatedExpr::errorMessage)
        ;

    boost::python::enum_<expr_boost_common::expr_data_model_type>("expr_data_model_type")
        .value("ADD", expr_boost_common::ADD)
        .value("BUILTIN_CONST", expr_boost_common::BUILTIN_CONST)
        .value("BUILTIN_FUNC", expr_boost_common::BUILTIN_FUNC)
        .value("DIVIDE", expr_boost_common::DIVIDE)
        .value("EQUALITY", expr_boost_common::EQUALITY)
        .value("EXPONENTIATION", expr_boost_common::EXPONENTIATION)
        .value("INEQUALITY", expr_boost_common::INEQUALITY)
        .value("FUNC_BEGIN", expr_boost_common::FUNC_BEGIN)
        .value("FUNC_END", expr_boost_common::FUNC_END)
        .value("FUNC_NAME", expr_boost_common::FUNC_NAME)
        .value("FUNC_ARG", expr_boost_common::FUNC_ARG)
        .value("GREATER_THAN", expr_boost_common::GREATER_THAN)
        .value("GREATER_THAN_OR_EQUAL", expr_boost_common::GREATER_THAN_OR_EQUAL)
        .value("LESS_THAN", expr_boost_common::LESS_THAN)
        .value("LESS_THAN_OR_EQUAL", expr_boost_common::LESS_THAN_OR_EQUAL)
        .value("LOGICAL_AND", expr_boost_common::LOGICAL_AND)
        .value("LOGICAL_OR", expr_boost_common::LOGICAL_OR)
        .value("MULTIPLY", expr_boost_common::MULTIPLY)
        .value("NUMBER", expr_boost_common::NUMBER)
        .value("PARAM_NAME", expr_boost_common::PARAM_NAME)
        .value("POWER", expr_boost_common::POWER)
        .value("SUBTRACT", expr_boost_common::SUBTRACT)
        .value("TERNARY_CONDITION", expr_boost_common::TERNARY_CONDITION)
        .value("TERNARY_LEFT", expr_boost_common::TERNARY_LEFT)
        .value("TERNARY_RIGHT", expr_boost_common::TERNARY_RIGHT)
        .value("UNARY_NEG", expr_boost_common::UNARY_NEG)
        .value("UNARY_POS", expr_boost_common::UNARY_POS)
        ;

    boost::python::class_<SpectreExprBoostParser>("SpectreExprBoostParser")
        .def("parseExpr", &SpectreExprBoostParser::parseExpr)
        .def_readwrite("py_dict", &SpectreExprBoostParser::dict)
        .def_readwrite("py_list", &SpectreExprBoostParser::list)
        .def_readwrite("py_list2", &SpectreExprBoostParser::list2)
        .def("import_func_statements", &SpectreExprBoostParser::import_func_statements)
        .def("import_func_args", &SpectreExprBoostParser::import_func_args)
        .def("import_param_statements", &SpectreExprBoostParser::import_param_statements)
        .def("eval_statements", &SpectreExprBoostParser::eval_statements)
        .def("print_maps", &SpectreExprBoostParser::print_maps)
        ;

    boost::python::class_<HSPICEExprBoostParser>("HSPICEExprBoostParser")
        .def("parseExpr", &HSPICEExprBoostParser::parseExpr)
        .def_readwrite("py_dict", &HSPICEExprBoostParser::dict)
        .def_readwrite("py_list", &HSPICEExprBoostParser::list)
        .def_readwrite("py_list2", &HSPICEExprBoostParser::list2)
        .def("import_func_statements", &HSPICEExprBoostParser::import_func_statements)
        .def("import_func_args", &HSPICEExprBoostParser::import_func_args)
        .def("import_param_statements", &HSPICEExprBoostParser::import_param_statements)
        .def("eval_statements", &HSPICEExprBoostParser::eval_statements)
        .def("print_maps", &HSPICEExprBoostParser::print_maps)
        ;
}
