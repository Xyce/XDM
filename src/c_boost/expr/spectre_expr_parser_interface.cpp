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


#include "spectre_expr_parser_interface.hpp"
#include "spectre_arithmetic_grammar.hpp"
#include <boost/algorithm/string.hpp>
#include <boost/python.hpp>
#include <boost/python/extract.hpp>
#include <boost/spirit/include/qi.hpp>
#include <iostream>


BoostParsedExpr SpectreExprBoostParser::parseExpr(std::string expr)
{
    namespace qi = boost::spirit::qi;
    namespace ascii = boost::spirit::ascii;

    BoostParsedExpr parsedExpr;
    parsedExpr.sourceLine = expr;

    std::string::const_iterator start = expr.begin();
    std::string::const_iterator end = expr.end();

    std::vector<expr_boost_common::expr_object> expr_parse_result;

    typedef ast_common::root ast_root;
    typedef std::string::const_iterator iterator_type;
    typedef SpectreArithmeticGrammar<iterator_type> grammar;
    grammar g;
    ast_root top;

    start = expr.begin();
    end = expr.end();
    ast_common::printer<grammar> print(variable_map, function_variable_map, function_map, g, expr_parse_result);
    bool r = phrase_parse(start, end, g, boost::spirit::ascii::space, top);
    print(top);

    if (r && start == end)
    {
        convert_to_parsed_objects(expr_parse_result, parsedExpr);
    }
    else
    {
        parsedExpr.errorType = "warn";
        parsedExpr.errorMessage = "\nSpectre Expression Parsing failed.";
    }

    return parsedExpr;
}

void SpectreExprBoostParser::import_func_statements(boost::python::dict & py_dict)
{
    Py_Initialize();

    std::cout << "Building function maps ... " << std::endl;

    boost::python::list items = py_dict.items();
    for(size_t i = 0; i < len(items); i++)
    {
        boost::python::object key = items[i][0];
        boost::python::object value = items[i][1];

        boost::python::extract<std::string> key_str(key);
        boost::python::extract<std::string> value_str(value);
        std::string k = key_str();
        std::string v = value_str();

        function_map[k] = v;
    }

    return;
}

void SpectreExprBoostParser::import_func_args(boost::python::dict & py_dict)
{
    Py_Initialize();

    std::cout << "Building function argument maps ... " << std::endl;

    boost::python::list items = py_dict.items();
    for(size_t i = 0; i < len(items); i++)
    {
        boost::python::object key = items[i][0];
        boost::python::extract<std::string> key_str(key);
        std::string k = key_str();

        boost::python::object args = items[i][1];
        for(size_t j = 0; j < len(args); j++)
        {
            boost::python::object value = args[j];
            boost::python::extract<std::string> value_str(value);
            std::string v = value_str();

            function_variable_map[k][j] = v;
        }
    }

    return;
}

void SpectreExprBoostParser::import_param_statements(boost::python::list & py_list)
{
    Py_Initialize();
    double out_val;
    std::vector<std::string> unresolved_param_list;
    int unresolved_count;
    typedef std::string::const_iterator iterator_type;
    typedef SpectreArithmeticGrammar<iterator_type> grammar;
    grammar g;

    std::cout << "Building parameter maps ... \n" << std::endl;

    for(size_t i = 0; i < len(py_list); i++)
    {
        boost::python::extract<std::string> value_str(py_list[i]);
        std::string param_name = value_str().substr(0, value_str().find("="));

        ast_common::process_input(value_str(), g, variable_map, function_variable_map, function_map, out_val);

        if(isnan(variable_map[param_name]) || isinf(variable_map[param_name]))
        {
            unresolved_param_list.push_back(value_str());
        }
        else
        {
            param_list.push_back(value_str());
        }
    }

    // SPICE doesn't care about ordering of parameters. So if a parameter
    // depends on a second parameter, that second parameter can appear after
    // the first. Because of this, there needs to be a re-processing to make
    // sure out of order parameters are evaluated correctly. This while loop
    // does that by continuing to process unresolved parameters until the
    // parameters cannot be resolved any further
    unresolved_count = unresolved_param_list.size();
    while(unresolved_count > 0)
    {
        std::vector<std::string> new_unresolved_param_list;
        int new_unresolved_count;

        for(int j = 0; j < unresolved_param_list.size(); j++)
        {
            std::string param_name = unresolved_param_list[j].substr(0, unresolved_param_list[j].find("="));

            ast_common::process_input(unresolved_param_list[j], g, variable_map, function_variable_map, function_map, out_val);

            if(isnan(variable_map[param_name]) || isinf(variable_map[param_name]))
            {
                new_unresolved_param_list.push_back(unresolved_param_list[j]);
            }
            else
            {
                param_list.push_back(unresolved_param_list[j]);
            }
        }

        new_unresolved_count = new_unresolved_param_list.size();

        // If no further resolutions, stop
        if(new_unresolved_count == unresolved_count)
        {
            std::cout << "Could not resolve the following expressions:" << std::endl;
            for(int j = 0; j < unresolved_param_list.size(); j++)
            {
                std::cout << j << " " << unresolved_param_list[j] << std::endl;
            }
            std::cout << "Continuing... " << std::endl;
            break;
        }
        else
        {
            unresolved_count = new_unresolved_count;
            unresolved_param_list = new_unresolved_param_list;
        }
    }

    return;
}

BoostEvaluatedExpr SpectreExprBoostParser::eval_statements(
    boost::python::list & py_list,
    boost::python::list & py_list_2)
{
    Py_Initialize();
    double out_val;
    typedef std::string::const_iterator iterator_type;
    typedef SpectreArithmeticGrammar<iterator_type> grammar;
    grammar g;
    BoostEvaluatedExpr output;

    for(size_t i = 0; i < len(py_list); i++)
    {
        boost::python::object hier_value = py_list[i];
        boost::python::object expr_value = py_list_2[i];

        boost::python::extract<std::string> hier_str(hier_value);
        std::string hier = hier_str();
        boost::python::extract<std::string> expr_str(expr_value);
        std::string expr = expr_str();

        std::cout << "Evaluating " << hier << " " << expr << " ... " << std::endl;

        std::string param_st;
        if(hier.find(":") != std::string::npos)
        {
            size_t equals_idx = hier.find_last_of(":");
            param_st = hier.substr(equals_idx+1);
            param_st += "=";
            param_st += expr;
        }
        else
        {
            param_st = hier;
            param_st += "=";
            param_st += expr;
        }

        ast_common::process_input(param_st, g, variable_map, function_variable_map, function_map, out_val);
        std::cout << "EVALUATION RESULT : " << hier << " " << expr << "-->" << out_val << "\n" << std::endl;

        output.evalResult.append(out_val);
    }

    return output;
}

void SpectreExprBoostParser::print_maps()
{
    std::cout << "\nFUNCTION_MAP" << std::endl;
    for(auto elem : function_map)
    {
        std::cout << elem.first << " " << elem.second << std::endl;
    }

    std::cout << "\nFUNCTION_VARIABLE_MAP" << std::endl;
    for(std::unordered_map<std::string, std::map<int, std::string> >::iterator outer_iter=function_variable_map.begin(); outer_iter!=function_variable_map.end(); ++outer_iter) 
    {
        for(std::map<int, std::string>::iterator inner_iter=outer_iter->second.begin(); inner_iter!=outer_iter->second.end(); ++inner_iter) 
        {
            std::cout << outer_iter->first << " " << inner_iter->second << std::endl;
        }
    }

    std::cout << "\nVARIABLE_MAP" << std::endl;
    for(auto elem : variable_map)
    {
        std::cout << elem.first << " " << elem.second << std::endl;
    }

    std::cout << "\nPARAM_LIST" << std::endl;
    for(auto elem : param_list)
    {
        std::cout << elem << std::endl;
    }

    return;
}
