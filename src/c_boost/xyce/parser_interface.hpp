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


#ifndef PARSER_INTERFACE_HPP
#define PARSER_INTERFACE_HPP


#include <boost/python.hpp>
#include "boost_adm_parser_common.h"
#include <boost/algorithm/string.hpp>
#include <string>
#include <vector>
#include <queue>
#include <fstream>
#include <iostream>


struct parse_results {
    int num_success_parsed_lines;
    int num_parsable_lines;
    double parse_time;
    bool isGoodParse;
};


struct BoostParsedLine {
    boost::python::list parsedObjects;
    boost::python::list linenums;
    std::string filename;
    std::string sourceLine;
    std::string errorType;
    std::string errorMessage;
};


struct ParseObject {
    std::string value;
    boost::python::list types;
};


// Takes in a parsed line object and returns the associated line numbers from the original
// file as a string (e.g. "[45,46,47]")
std::string getLineNumsString (BoostParsedLine parsedLine);

// Identifies if an inline comment is present based on grammar, 
// returns the line with the inline comment stripped from it
template <typename Grammar>
std::string stripInlineCommentString(std::string line, Grammar const&g) {
    std::string::const_iterator start = line.begin();
    std::string::const_iterator end = line.end();
    std::string currentInlineComment = "";
    std::string inlineCommentIdentifier = "INLINE_COMMENT";
    std::vector<std::string> results;
    std::string rtnLine;
    std::vector<adm_boost_common::netlist_statement_object> netlist_parse_results;

    bool r = phrase_parse(start, end, g, boost::spirit::ascii::space, netlist_parse_results);
    for(int i = 0; i < netlist_parse_results.size(); i++) {
        std::string dataModelType = adm_boost_common::getDataModelTypeStr(netlist_parse_results[i]);

        if (dataModelType == inlineCommentIdentifier){
            currentInlineComment = netlist_parse_results[i].value;
        }
     }

    rtnLine = line;
    if (currentInlineComment != ""){
        boost::iter_split(results, line, boost::algorithm::first_finder(currentInlineComment));
        rtnLine = results[0];
    }

    return rtnLine;
}

struct NetlistLineReader {

    std::ifstream * inputStream;
    std::string filename;
    std::string title;

    std::string tmp_line;
    int current_line_num;

    std::queue<BoostParsedLine> lines;

    bool open(std::string filenm);

    void close();

    template <typename Grammar>
    void read_next_parsable_line(Grammar const& g) {
    
        BoostParsedLine parsedLine;
        parsedLine.filename = filename;
        std::string currentRtnLine, nextRtnLine;
    
        if(!inputStream->good()) {
            if(tmp_line != "") {
                parsedLine.sourceLine = tmp_line;
                parsedLine.linenums.append(current_line_num);
                lines.push(parsedLine);
            }
            tmp_line = "";
            return;
        }
    
        std::string line_next = "";
    
        if(tmp_line.empty()) {
            //find start of next parsable line
            while(line_next.empty() && !inputStream->eof()) {
                getline(*inputStream, line_next);
                boost::trim(line_next);
                current_line_num++;
            }
        } else {
            line_next = tmp_line;
            tmp_line = "";
        }
    
        parsedLine.sourceLine = line_next;
        parsedLine.linenums.append(current_line_num);

        bool foundEnd = false;
        std::string origCommandLine = "";
        std::string tmpOrigCommandLine = stripInlineCommentString(parsedLine.sourceLine, g);
        boost::trim_right(tmpOrigCommandLine);
        std::string tmpCommandLine;
        std::vector<std::string> results;

        while(!foundEnd && !inputStream->eof()) {
    
            getline(*inputStream, line_next);
            boost::trim(line_next);
            current_line_num++;
    
            tmp_line = line_next;
    
            if(line_next.empty()) continue;

            if(boost::starts_with(line_next, "*") || boost::starts_with(line_next, "//") || boost::starts_with(line_next, "$")) {
                BoostParsedLine commentLine;
                commentLine.filename = filename;
                commentLine.sourceLine = line_next;
                commentLine.linenums.append(current_line_num);
                lines.push(commentLine);
                tmp_line = "";
            }
            // For case of dangling parentheses in .MODEL statements, allowable in HSPICE/PSPICE
            else if(boost::starts_with(line_next, ")")) {
                currentRtnLine = stripInlineCommentString(parsedLine.sourceLine, g);
                boost::trim_right(currentRtnLine);
                parsedLine.sourceLine = currentRtnLine + " " + line_next;
            }
            // only considers "+" as line continuation if current line doesn't end with a "\\" line continuation
            // Need to save original, first portion of the line with the command statement (.PARAM for instance)
            // if it hasn't been done. The next line needs to be checked for inline comments as well.
            // If this is not the original, first part of the line with the command statement,
            // then the current line is just appended to the original portion for inline comment checking purposes.
            else if(boost::starts_with(line_next, "+") && !boost::ends_with(parsedLine.sourceLine, "\\")) {
                if (origCommandLine.empty()) {
                    origCommandLine = tmpOrigCommandLine;
                    currentRtnLine = stripInlineCommentString(parsedLine.sourceLine, g);
                    boost::trim_right(currentRtnLine);
                    parsedLine.sourceLine = currentRtnLine + " " + line_next.substr(1);
                    currentRtnLine = stripInlineCommentString(parsedLine.sourceLine, g);
                    boost::trim_right(currentRtnLine);
                    parsedLine.sourceLine = currentRtnLine;
                }
                else {
                    tmpCommandLine = origCommandLine + " " + line_next.substr(1);
                    currentRtnLine = stripInlineCommentString(tmpCommandLine, g);
                    boost::trim_right(currentRtnLine);
                    boost::iter_split(results, currentRtnLine, boost::algorithm::first_finder(origCommandLine));
                    parsedLine.sourceLine = parsedLine.sourceLine + " " + results[1];
                }
                boost::trim_right(parsedLine.sourceLine);
                parsedLine.linenums.append(current_line_num);
                tmp_line = "";
            }
            // must check case of "\\" continuation first in order to avoid going into "\" block mistakenly
            // inline comments cannot occur after in-expression continuation character "\\" in HSPICE. So only need
            // to remove "\\" from line, and append to original line. 
            else if (boost::ends_with(parsedLine.sourceLine, R"delim(\\)delim")) {
                // need to trim "\\" line continuation characters
                parsedLine.sourceLine.pop_back();
                parsedLine.sourceLine.pop_back();
                boost::trim(line_next);
                // current line and next line need to be joined with no spaces
                parsedLine.sourceLine = parsedLine.sourceLine + line_next;
                if (origCommandLine.empty()) {
                    tmpOrigCommandLine = parsedLine.sourceLine;
                } 
                boost::trim_right(parsedLine.sourceLine);
                parsedLine.linenums.append(current_line_num);
            }
            // Block to check for line continuation using "\" character.
            // Same as in two blocks above: need to save original, first portion of the line with 
            // the command statement (.PARAM for instance) if it hasn't been done. The next line needs to be checked for
            // inline comments as well.
            // If this is not the original, first part of the line with the command statement,
            // then the current line is just appended to the original portion for inline comment checking purposes.
            else {
                if (origCommandLine.empty()) {
                    currentRtnLine = stripInlineCommentString(parsedLine.sourceLine, g);
                    boost::trim_right(currentRtnLine);
                }
                else {
                    currentRtnLine = parsedLine.sourceLine;
                }

                if (boost::ends_with(currentRtnLine, R"delim(\)delim")) {
                    if (origCommandLine.empty()) {
                        origCommandLine = tmpOrigCommandLine;
                        currentRtnLine.pop_back();
                        boost::trim(line_next);
                        parsedLine.sourceLine = currentRtnLine + " " + line_next;
                        currentRtnLine = stripInlineCommentString(parsedLine.sourceLine, g);
                        boost::trim_right(currentRtnLine);
                        parsedLine.sourceLine = currentRtnLine;
                    }
                    else {
                        parsedLine.sourceLine.pop_back();
                        boost::trim(line_next);
                        tmpCommandLine = origCommandLine + " " + line_next;
                        currentRtnLine = stripInlineCommentString(tmpCommandLine, g);
                        boost::trim_right(currentRtnLine);
                        boost::iter_split(results, currentRtnLine, boost::algorithm::first_finder(origCommandLine));
                        parsedLine.sourceLine = parsedLine.sourceLine + " " + results[1];
                    }
                    boost::trim_right(parsedLine.sourceLine);
                    parsedLine.linenums.append(current_line_num);
                }
                else {
                    foundEnd = true;
                }
            }
        }
    
        lines.push(parsedLine);
    }

    template <typename Grammar>
    bool hasNext(Grammar const& g) {
        read_next_parsable_line(g);
        return lines.size() > 0;
    }


    template <typename Grammar>
    BoostParsedLine next(Grammar const& g){
        read_next_parsable_line(g);
        BoostParsedLine rtn = lines.front();
        lines.pop();
        return rtn;
    }

};


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// PYTHON INTERFACE
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void convert_to_parsed_objects(std::vector<adm_boost_common::netlist_statement_object> netlist_parse_results, BoostParsedLine parsedLine);


inline boost::python::object pass_through(boost::python::object const& o) { return o; }


#endif
