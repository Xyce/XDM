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
