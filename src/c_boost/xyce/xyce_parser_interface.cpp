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


#include "xyce_parser_interface.hpp"
#include "XyceParser.hpp"
#include <iostream>
#include <string>

bool
XyceNetlistBoostParser::open(std::string filenm, bool top_level_file) {
    this->is_top_level_file = top_level_file;
    return reader.open(filenm);
}

void
XyceNetlistBoostParser::close() {
    reader.close();
}


BoostParsedLine
XyceNetlistBoostParser::next() {

    typedef xyce_parser<iterator_type> xyce_parser;
    xyce_parser g;

    if(!reader.hasNext(g)) {
        PyErr_SetString(PyExc_StopIteration, "No more data.");
        boost::python::throw_error_already_set();
    }

    BoostParsedLine parsedLine = reader.next(g);

    if(is_top_level_file && parsedLine.linenums[0] == 1) {
        adm_boost_common::netlist_statement_object titleNSO;
        titleNSO.value = "*" + parsedLine.sourceLine;
        titleNSO.candidate_types.push_back(adm_boost_common::TITLE);

        std::vector<adm_boost_common::netlist_statement_object> v;
        v.push_back(titleNSO);

        convert_to_parsed_objects(v, parsedLine);
    } else {
        parseLine(parsedLine);
    }

    return parsedLine;
}

void
XyceNetlistBoostParser::parseLine(BoostParsedLine & parsedLine) {

    //setup parser objects
    //typedef std::string::const_iterator iterator_type;
    typedef xyce_parser<iterator_type> xyce_parser;
    xyce_parser g;

    std::string::const_iterator start = parsedLine.sourceLine.begin();
    std::string::const_iterator end = parsedLine.sourceLine.end();

    std::vector<adm_boost_common::netlist_statement_object> netlist_parse_results;
    // Note phrase_parse is a call supplied by boost::spirit::qi
    bool r = phrase_parse(start, end, g, boost::spirit::ascii::space, netlist_parse_results);

    if (r && start == end)
    {
        //std::cout << "Xyce Parsing succeeded: \n" << parsedLine.sourceLine << std::endl;
        //for(int i = 0; i < netlist_parse_results.size(); i++) {
        //std::cout << netlist_parse_results[i] << std::endl;
        //}
        //std::cout << "\n\n" << std::flush;

        convert_to_parsed_objects(netlist_parse_results, parsedLine);
    } else {
        //std::cout << "Xyce Parsing failed: \n" << parsedLine.sourceLine << std::endl;
        //for(int i = 0; i < netlist_parse_results.size(); i++) {
        //std::cout << netlist_parse_results[i] << std::endl;
        //}
        //std::cout << "bool r = " << r << std::endl;
        //std::cout << "\n\n" << std::flush;

        netlist_parse_results.clear();
        // if parsing the string failed, we turn it into a comment and report the line numbers
        parsedLine.sourceLine = "* " + parsedLine.sourceLine + "; Xyce Parser Retained (as a comment). Continuing.";
        start = parsedLine.sourceLine.begin();
        end = parsedLine.sourceLine.end();
        parsedLine.errorType = "warn";
        parsedLine.errorMessage = parsedLine.sourceLine;
        bool comment_readable = phrase_parse(start, end, g, boost::spirit::ascii::space, netlist_parse_results);
        if (comment_readable){
            convert_to_parsed_objects(netlist_parse_results, parsedLine);
        } else {
            std::cout << "\nXyce Parsing failed around line " + getLineNumsString (parsedLine) +
                " and line(s) could not be converted to comment\n" << std::endl;
        }
    }
}
