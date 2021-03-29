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


#if !defined(BOOST_SPIRIT_PSPICE2)
#define BOOST_SPIRIT_PSPICE2

#include "XyceParser.hpp"

template <typename Iterator>
struct pspice_parser : qi::grammar<Iterator, std::vector<netlist_statement_object>()>
{
    qi::rule<Iterator, std::vector<netlist_statement_object>()> aliases_dir, distribution_dir, endaliases_dir, loadbias_dir, mc_dir, noise_dir,
        plot_dir, savebias_dir, stimulus_dir, text_dir, tf_dir, vector_dir, watch_dir, wcase_dir, pspice_start, lib_dir, options_dir, print_dir,
        probe_dir, temp_dir, tran_dir, directive, probe_64_dir, nodeset_dir, autoconverge_dir;

    qi::rule<Iterator, netlist_statement_object()> aliases_dir_type, distribution_dir_type, endaliases_dir_type, loadbias_dir_type, mc_dir_type,
        noise_dir_type, plot_dir_type, savebias_dir_type, stimulus_dir_type, text_dir_type, tf_dir_type, vector_dir_type, watch_dir_type,
        wcase_dir_type, tran_op_type, probe_dir_type,  probe_csdf_type, temp_dir_type, output_variable, TEMP_VALUE, probe_64_dir_type, nodeset_dir_type,
        autoconverge_dir_type;

    qi::rule<Iterator, std::string()> output_variable_expression, output_variable_node;

    xyce_parser<iterator_type> base_parser;

    pspice_parser() : pspice_parser::base_type(pspice_start)
    {
        using qi::lit;
        using qi::char_;
        using qi::lexeme;
        using qi::hold;
        using ascii::alnum;
        using ascii::string;
        using ascii::no_case;
        using namespace qi::labels;

        // CORE TERMINALS

        TEMP_VALUE =
            base_parser.identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::TEMP_VALUE))]
            ;

        output_variable_expression =
            hold[no_case[char_("N")] >> no_case[char_("O")] >> no_case[char_("I")] >> no_case[char_("S")] >> no_case[char_("E")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("V")] >> no_case[char_("B")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("V")] >> no_case[char_("B")] >> no_case[char_("E")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("V")] >> no_case[char_("D")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("V")] >> no_case[char_("G")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("V")] >> no_case[char_("S")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("V")] >> no_case[char_("A")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("V")] >> no_case[char_("B")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("V")] >> char_("(") >> -char_("[") >>  base_parser.identifier >> char_(",") >>  base_parser.identifier >> -char_("]") >> char_(")")] |
            hold[no_case[char_("I")] >> no_case[char_("B")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("I")] >> no_case[char_("D")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("I")] >> no_case[char_("G")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("I")] >> no_case[char_("S")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("I")] >> no_case[char_("A")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("I")] >> no_case[char_("B")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("I")] >> +char_("0-9") >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("I")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")]  |
            hold[no_case[char_("D")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("W")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("V")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")] |
            hold[no_case[char_("N")] >> char_("(") >> -char_("[") >> output_variable_node >> -char_("]") >> char_(")")]
            ;

        output_variable =
            output_variable_expression [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::OUTPUT_VARIABLE))]
            ;

        // lit is used because we do not want it passed up -- alias() is an artifact of pspice and should be ignored
        output_variable_node =
            hold[-base_parser.white_space >> no_case[lit("alias")] >> lit("(") >> -base_parser.white_space >> base_parser.identifier >> -base_parser.white_space >> lit(")") >> -base_parser.white_space] |
            -base_parser.white_space >> base_parser.identifier >> -base_parser.white_space
            ;

        // STARTING POINT ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        pspice_start = (directive >> -(-base_parser.white_space >> base_parser.inline_comment)) | base_parser.netlist_line
            ;

        // DIRECTIVES ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        directive =
            probe_64_dir | lib_dir | options_dir | print_dir | probe_dir | temp_dir | tran_dir | aliases_dir | distribution_dir | endaliases_dir |
            loadbias_dir | mc_dir | noise_dir | plot_dir | savebias_dir | stimulus_dir | text_dir | tf_dir | vector_dir | watch_dir |
            wcase_dir | nodeset_dir | autoconverge_dir
            ;

        lib_dir =
            base_parser.lib_dir_type >>  base_parser.white_space >> base_parser.filename
            ;

        options_dir =
            hold[base_parser.options_dir_type >> +( base_parser.white_space >> base_parser.param_value_pair)] |
            hold[base_parser.options_dir_type >> base_parser.white_space >> base_parser.default_param_name]
            ;

        print_dir =
            base_parser.print_dir_type >> base_parser.white_space >> base_parser.analysis_type >> *(base_parser.white_space >> !output_variable >> base_parser.param_value_pair) >> +(base_parser.white_space >> output_variable)
            ;

        probe_dir_type =
            qi::as_string[no_case[lit(".PROBE")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        probe_csdf_type =
            qi::as_string[no_case[lit("/CSDF")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::PARAM_VALUE))]
            ;

        probe_dir =
            probe_dir_type >> -probe_csdf_type >> *( base_parser.white_space >> output_variable)
            ;

        probe_64_dir_type =
            qi::as_string[no_case[lit(".PROBE64")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        probe_64_dir =
            probe_64_dir_type >> *( base_parser.white_space >> output_variable)
            ;

        temp_dir_type =
            qi::as_string[no_case[lit(".TEMP")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        temp_dir =
            temp_dir_type >> *( base_parser.white_space >> base_parser.list_param_value)
            ;

        tran_op_type =
            qi::as_string[no_case[lit("/OP")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::PARAM_VALUE))]
            ;

        tran_dir =
            base_parser.tran_dir_type >> -tran_op_type >> base_parser.white_space >> base_parser.printStepValue >> base_parser.white_space >> base_parser.finalTimeValue >> -(base_parser.white_space >> base_parser.startTimeValue >> -(base_parser.white_space >> base_parser.stepCeilingValue)) //need to handle schedule
            ;

        // UNSUPPORTED DIRECTIVES ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        aliases_dir_type =
            qi::as_string[no_case[lit(".ALIASES")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        autoconverge_dir_type =
            qi::as_string[no_case[lit(".AUTOCONVERGE")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        distribution_dir_type =
            qi::as_string[no_case[lit(".DISTRIBUTION")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        endaliases_dir_type =
            qi::as_string[no_case[lit(".ENDALIASES")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        loadbias_dir_type =
            qi::as_string[no_case[lit(".LOADBIAS")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        mc_dir_type =
            qi::as_string[no_case[lit(".MC")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        noise_dir_type =
            qi::as_string[no_case[lit(".NOISE")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        plot_dir_type =
            qi::as_string[no_case[lit(".PLOT")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        savebias_dir_type =
            qi::as_string[no_case[lit(".SAVEBIAS")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        stimulus_dir_type =
            qi::as_string[no_case[lit(".STIMULUS")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        text_dir_type =
            qi::as_string[no_case[lit(".TEXT")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        tf_dir_type =
            qi::as_string[no_case[lit(".TF")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        vector_dir_type =
            qi::as_string[no_case[lit(".VECTOR")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        watch_dir_type =
            qi::as_string[no_case[lit(".WATCH")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        wcase_dir_type =
            qi::as_string[no_case[lit(".WCASE")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        nodeset_dir_type =
            qi::as_string[no_case[lit(".NODESET")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        aliases_dir =
            aliases_dir_type >> base_parser.restOfLine
            ;

        autoconverge_dir =
            autoconverge_dir_type >> base_parser.restOfLine
            ;

        distribution_dir =
            distribution_dir_type >> base_parser.restOfLine
            ;

        endaliases_dir =
            endaliases_dir_type >> base_parser.restOfLine
            ;

        loadbias_dir =
            loadbias_dir_type >> base_parser.restOfLine
            ;

        mc_dir =
            mc_dir_type >> base_parser.restOfLine
            ;

        noise_dir =
            noise_dir_type >> base_parser.restOfLine
            ;

        plot_dir =
            plot_dir_type >> base_parser.restOfLine
            ;

        savebias_dir =
            savebias_dir_type >> base_parser.restOfLine
            ;

        stimulus_dir =
            stimulus_dir_type >> base_parser.restOfLine
            ;

        text_dir =
            text_dir_type >> base_parser.restOfLine
            ;

        tf_dir =
            tf_dir_type >> base_parser.restOfLine
            ;

        vector_dir =
            vector_dir_type >> base_parser.restOfLine
            ;

        watch_dir =
            watch_dir_type >> base_parser.restOfLine
            ;

        wcase_dir =
            wcase_dir_type >> base_parser.restOfLine
            ;

        nodeset_dir =
            nodeset_dir_type >>
            hold[+(base_parser.white_space >> -base_parser.voltage_type >> -base_parser.white_space >> -lit("(") >>
                    -base_parser.white_space >> -lit("[") >> -base_parser.white_space >> base_parser.general_node >> -base_parser.white_space >>
                    -lit("]") >> -base_parser.white_space >> -lit(")")) >> -base_parser.white_space >> -lit("=") >> -base_parser.white_space >>
            base_parser.GENERAL_VALUE]
            ;
    }
};

#endif
