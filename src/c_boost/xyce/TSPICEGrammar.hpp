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


#if !defined(BOOST_SPIRIT_TSPICE)
#define BOOST_SPIRIT_TSPICE

#include "XyceParser.hpp"
#include "boost_adm_parser_common.h"
#include <unordered_map>

namespace qi = boost::spirit::qi;
namespace ascii = boost::spirit::ascii;

using namespace adm_boost_common;

template <typename Iterator>
struct tspice_parser : qi::grammar<Iterator, std::vector<netlist_statement_object>()>
{
    //netlist statement objects
    qi::rule<Iterator, std::vector<netlist_statement_object>()>
        bjt, capacitor, current_ctrl_current_src, current_ctrl_switch, current_ctrl_voltage_src, diode, inductor, resistor, indep_current_src,
        indep_voltage_src, jfet, mosfet, subcircuit, voltage_ctrl_current_src, voltage_ctrl_voltage_src, mesfet, lossy_trans_line, voltage_ctrl_resistor//, coupled_trans_line
            //devices that are different
            ;

    qi::rule<Iterator, std::vector<netlist_statement_object>()>
        acmodel_dir, alter_dir, assert_dir, checkpoint_dir, connect_dir, data_dir, enddata_dir, dellib_dir, global_dir, hdl_dir,
        if_dir, else_dir, elseif_dir, endif_dir, lib_dir, load_dir, malias_dir, optgoal_dir, optimize_dir, paramlimits_dir, power_dir,
        probe_dir, protect_dir, unprotect_dir, savebias_dir, temp_dir, tf_dir, vector_dir, warn_dir, gridsize_dir, table_dir, vrange_dir,
        subckt_dir, ends_dir, ac_dir, dc_dir, ic_dir, nodeset_dir, print_dir, options_dir, four_dir, measure_dir, step_dir, tran_dir, tspice_start, directive
            //directives not to be overwritten: end_dir, endl_dir, include_dir, lib_dir, model_dir, noise_dir?, op_dir, param_dir
            ;

    qi::rule<Iterator, netlist_statement_object()>
        acmodel_dir_type, alter_dir_type, assert_dir_type, checkpoint_dir_type, connect_dir_type, data_dir_type, enddata_dir_type, dellib_dir_type,
        global_dir_type, hdl_dir_type, if_dir_type, else_dir_type, elseif_dir_type, endif_dir_type, load_dir_type, malias_dir_type,
        optgoal_dir_type, optimize_dir_type, paramlimits_dir_type, power_dir_type, probe_dir_type, protect_dir_type, unprotect_dir_type, savebias_dir_type,
        temp_dir_type, tf_dir_type, vector_dir_type, warn_dir_type, subckt_dir_type, ends_dir_type, gridsize_dir_type, table_dir_type, vrange_dir_type, measure_dir_type, measurement_type,
        output_variable, analysis_type, inline_comment, comment
            //types and variables and devices that need to be overwritten or added
            ;

    qi::rule<Iterator, std::string()> inline_comment_str, comment_str, output_variable_expression;

    xyce_parser<iterator_type> base_parser;

    tspice_parser() : tspice_parser::base_type(tspice_start)
    {
        using qi::lit;
        using qi::char_;
        using qi::as_string;
        using qi::lexeme;
        using qi::hold;
        using ascii::alnum;
        using ascii::string;
        using ascii::no_case;
        using namespace qi::labels;

        //Variables and Types
        measurement_type =
            (qi::as_string[no_case[lit("AVG")]] |
             qi::as_string[no_case[lit("AMAX")]] |
             qi::as_string[no_case[lit("AMIN")]] |
             qi::as_string[no_case[lit("DERIVATIVE")]] |
             qi::as_string[no_case[lit("ERR")]] |
             qi::as_string[no_case[lit("ERR1")]] |
             qi::as_string[no_case[lit("ERR2")]] |
             qi::as_string[no_case[lit("ERR3")]] |
             qi::as_string[no_case[lit("FIND")]] |
             qi::as_string[no_case[lit("INTEGRAL")]] |
             qi::as_string[no_case[lit("MAX")]] |
             qi::as_string[no_case[lit("MIN")]] |
             qi::as_string[no_case[lit("PP")]] |
             qi::as_string[no_case[lit("RMS")]] |
             qi::as_string[no_case[lit("TARG")]] |
             qi::as_string[no_case[lit("TRIG")]] |
             qi::as_string[no_case[lit("WHEN")]])[symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::ANALYSIS_TYPE))]
            ;

        analysis_type =
            (qi::as_string[no_case[lit("DC")]] |
             qi::as_string[no_case[lit("AC")]] |
             qi::as_string[no_case[lit("TRAN")]] |
             qi::as_string[no_case[lit("NOISE")]])[symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::ANALYSIS_TYPE))]
            ;

        output_variable_expression =
            hold[-base_parser.white_space >> base_parser.identifier >> -base_parser.white_space] |
            hold[no_case[char_("i")] >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("i")] >> +char_("BbCcDdEeGgNnPpSs1234") >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("i")] >> +char_("0-9") >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("p")] >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("q")] >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("q")] >> +char_("BbCcDdEeGgNnPpSs1234") >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("v")] >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[char_("'") >> *(char_) >> lit("time()") >> *(char_) >> char_("'")] |
            hold[no_case[char_("i")] >> no_case[char_("d")] >> no_case[char_("b")] >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("i")] >> no_case[char_("d")] >> no_case[char_("b")] >> +char_("BbCcDdEeGgNnPpSs1234") >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("i")] >> no_case[char_("i")] >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("i")] >> no_case[char_("i")] >> +char_("BbCcDdEeGgNnPpSs1234") >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("i")] >> no_case[char_("m")] >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("i")] >> no_case[char_("m")] >> +char_("BbCcDdEeGgNnPpSs1234") >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("i")] >> no_case[char_("r")] >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("i")] >> no_case[char_("r")] >> +char_("BbCcDdEeGgNnPpSs1234") >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("i")] >> no_case[char_("p")] >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("i")] >> no_case[char_("p")] >> +char_("BbCcDdEeGgNnPpSs1234") >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("v")] >> no_case[char_("m")] >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("v")] >> no_case[char_("r")] >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("v")] >> no_case[char_("i")] >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("v")] >> no_case[char_("p")] >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[no_case[char_("v")] >> no_case[char_("d")] >> no_case[char_("b")] >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[char_("'") >> -(*(char_)) >> lit("frequency()") >> -(*(char_)) >> char_("'")] |
            hold[no_case[lit("dn")] >> char_("(") >> -base_parser.white_space >> base_parser.identifier >> -(-base_parser.white_space >> char_(",") >> -base_parser.white_space >> base_parser.identifier) >> -base_parser.white_space >> char_(")")] |
            hold[no_case[lit("inoise")]] |
            hold[no_case[lit("inoise")] >> char_("(") >> -base_parser.white_space >> no_case[lit("db")] >> -base_parser.white_space >> char_(")")] |
            hold[no_case[lit("inoise")] >> char_("(") >> -base_parser.white_space >> no_case[lit("tot")] >> -base_parser.white_space >> char_(")")] |
            hold[no_case[lit("onoise")]] |
            hold[no_case[lit("onoise")] >> char_("(") >> -base_parser.white_space >> no_case[lit("db")] >> -base_parser.white_space >> char_(")")] |
            hold[no_case[lit("onoise")] >> char_("(") >> -base_parser.white_space >> no_case[lit("tot")] >> -base_parser.white_space >> char_(")")] |
            hold[no_case[lit("transfer")]] |
            hold[no_case[char_("V")] >> char_("(") >> base_parser.identifier >> char_(")")]
            ;

        output_variable =
            output_variable_expression [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::OUTPUT_VARIABLE))]
            ;

        //comments
        inline_comment_str =
            (char_(";") >> *(char_)) | (char_("$") >> *(char_))
            ;

        comment_str =
            (char_(";") >> *(char_)) | (char_("*") >> *(char_)) | (char_("$") >> *(char_))
            ;
        //TSPICE has multiline comments /* */ /*is this implemented correctly?
        //will work for inline /*  and for 2 line /* ...  but not for more than 2 lines (lines inbetween are not commented)
        /*inline_comment =
          inline_comment_str[symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::INLINE_COMMENT))]
          ;*/

        comment =
            (comment_str) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::COMMENT))]
            ;

        //starting point
        tspice_start = (directive >> -(-base_parser.white_space >> base_parser.inline_comment)) | base_parser.netlist_line
            ;
        //tspice_start = (base_parser.directive >> -(-base_parser.white_space >> base_parser.inline_comment)) | base_parser.netlist_line;

        //Directives that are different
        directive =
            lib_dir | base_parser.directive
            // acmodel_dir | alter_dir | assert_dir | checkpoint_dir | connect_dir | data_dir | enddata_dir | dellib_dir | global_dir | hdl_dir |
            // if_dir | else_dir | elseif_dir | endif_dir | lib_dir | load_dir | malias_dir | optgoal_dir | optimize_dir | paramlimits_dir | power_dir |
            // probe_dir | protect_dir | unprotect_dir | savebias_dir | temp_dir | tf_dir | vector_dir | warn_dir | gridsize_dir | table_dir | vrange_dir | ac_dir | dc_dir | ic_dir | nodeset_dir | print_dir | subckt_dir | ends_dir |
            // four_dir | options_dir | measure_dir | step_dir | tran_dir
            ;

        //Aliases in TSPICE .macro = .subckt and .eom = .ends
        subckt_dir_type =
            qi::as_string[no_case[lit(".SUBCKT")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))] |
            qi::as_string[no_case[lit(".MACRO")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        subckt_dir =
            hold[subckt_dir_type >> base_parser.white_space >> base_parser.devname >> +(base_parser.white_space >> !base_parser.params_set_type >> base_parser.subckt_directive_param_value) >> -(base_parser.white_space >> base_parser.params_set_type >> +(base_parser.white_space >> base_parser.param_value_pair))] |
            hold[subckt_dir_type >> base_parser.white_space >> base_parser.devname >> +(base_parser.white_space >> !base_parser.param_value_pair >> base_parser.subckt_directive_param_value) >> *(base_parser.white_space >> base_parser.param_value_pair)]
            ;

        ends_dir_type =
            qi::as_string[no_case[lit(".ENDS")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))] |
            qi::as_string[no_case[lit(".EOM")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        ends_dir =
            ends_dir_type >> -(base_parser.white_space >> base_parser.param_value)
            ;

        //overwritten commands
        ac_dir =
            base_parser.ac_dir_type >> base_parser.white_space >> (base_parser.lin_sweep_type | base_parser.dec_sweep_type | base_parser.oct_sweep_type) >> base_parser.white_space >> base_parser.points_value >> base_parser.white_space >> base_parser.start_freq_value >> base_parser.white_space >> base_parser.end_freq_value >> base_parser.restOfLine |
            base_parser.ac_dir_type >> base_parser.restOfLine
            //Xyce does not support list or poi with .ac, user should be warned
            ;

        dc_dir =
            base_parser.dc_dir_type >> base_parser.white_space >> base_parser.FREQ_VALUE >> *(base_parser.white_space >> output_variable) >> base_parser.restOfLine
            //Xyce does not support number of frequencies, number of points or interpolation
            ;

        ic_dir =
            base_parser.ic_dir_type >> base_parser.white_space >> +(-base_parser.voltage_type >> -base_parser.white_space >> -lit("(") >> -base_parser.white_space >> base_parser.general_node >> -base_parser.white_space >> -lit(",") >> -base_parser.white_space >> -base_parser.general_node >> -lit(")") >> -base_parser.white_space >> lit("=") >> -base_parser.white_space >> base_parser.GENERAL_VALUE >> -lit(",") >> -base_parser.white_space) |
            base_parser.ic_dir_type >> base_parser.restOfLine
            //Xyce does not support setting inductor currents, user should be warned
            ;

        nodeset_dir =
            base_parser.nodeset_dir_type >> base_parser.white_space >> +(-base_parser.voltage_type >> -base_parser.white_space >> -lit("(") >> -base_parser.white_space >> base_parser.general_node >> -base_parser.white_space >> -lit(")") >> -base_parser.white_space >> -lit("=") >> -base_parser.white_space >> base_parser.GENERAL_VALUE >> -base_parser.white_space >> -lit(",") >> -base_parser.white_space)
            ; //TSPICE can set multiple nodes in one line

        //op_dir is the same except TSPICE has a [noprint] option that will stop op from printing, throw up warning for user?

        //param_dir is the same, except Xyce doesn't support Monte Carlo Definition or Optimization

        //model_dir in Xyce does not support opt/ako (optimization) like TSPICE does

        //noise_dir not fully supported in Xyce (should I include?)

        //save_dir, end_dir, endl_dir, include_dir, and lib_dir are the same in TSPICE and Xyce

        //print_dir would be the same if noise was implemented as an analysis_type in XyceParser (noise is a valid analysis type in Xyce so it should be?)
        print_dir =
            base_parser.print_dir_type >> base_parser.white_space >> analysis_type >> hold[*(base_parser.white_space >> base_parser.param_value_pair)] >> *(base_parser.white_space >> output_variable)
            ;

        four_dir =
            base_parser.four_dir_type >> base_parser.white_space >> base_parser.FREQ_VALUE >> *(base_parser.white_space >> output_variable) >> *(base_parser.white_space >> base_parser.param_value_pair)
            ;

        options_dir =
            base_parser.options_dir_type >> base_parser.white_space >> +(base_parser.white_space >> base_parser.param_value_pair)
            ;

        measure_dir_type =
            (qi::as_string[no_case[lit(".MEASURE")]] | qi::as_string[no_case[lit(".MEAS")]])[symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        measure_dir =
            hold[measure_dir_type >> base_parser.white_space >> analysis_type >> base_parser.white_space >> base_parser.result_name_value >> +(base_parser.white_space >> measurement_type >> +(base_parser.white_space >> output_variable >> -(lit("=") >> base_parser.param_value))) >> *(base_parser.white_space >> base_parser.param_value_pair)] |
            hold[measure_dir_type >> base_parser.white_space >> analysis_type >> base_parser.white_space >> base_parser.result_name_value >> base_parser.white_space >> measurement_type >> base_parser.white_space >> base_parser.param_value >> base_parser.white_space >> measurement_type >> output_variable >> *(base_parser.white_space >> base_parser.param_value_pair)]
            ;
        /*
        // ****TO IMPLEMENT****
        //.tran
        //Xyce: .TRAN S L [start time value [step ceiling value]] [NOOP] {UIC] [{schedule( time, max time step, ..)}]
        //TSPICE: .tran[/mode] S L [start=A] [UIC] [restart] [restarttime=time] [restartfile=file] [SWEEP sweep]
        //		mode: op, powerup or preview, S=max step time, L=total sim time, sweep uses .step syntax
        tran_dir =
        base_parser.tran_dir_type >> -(lit("/") >> qi::as_string[no_case[lit("op")]] | qi::as_string[no_case[lit("powerup")]] | qi::as_string[no_case[lit("preview")]]) >> base_parser.white_space >> base_parser.stepCeilingValue >> base_parser.white_space >> base_parser.finalTimeValue >> -(base_parser.white_space >> qi::as_string[no_case[lit("start")]] >> -(base_parser.white_space) >> lit("=") >> -(base_parser.white_space) >> base_parser.startTimeValue) >> -(base_parser.white_space >> base_parser.UIC_VALUE) >> base_parser.restOfLine
        ;//Xyce can do nothing with restart or sweep parameters*/

        //.step:
        //Xyce: .step <parameter name> <initial> <final> <step> or .step DEC/OCT <sweep param name> <start> <stop> <points> or .step <sweep variable name> LIST <val> ... [<sweep param name> <val> ...]
        //TSPICE: .step sweep [[SWEEP] sweep [[SWEEP] sweep]] where sweep is [LIN] <points> <start> <stop> or DEC/OCT <variable name> <start> <stop> <points> or <variable> LIN/DEC/OCT <points> <start> <stop>
        //				or <variable> LIST <val> ... or LIST <variable> <val> ... Xyce does not support POI, DATA, MONTE, or OPTIMIZE, comment out and warn user
        step_dir =
            hold[base_parser.step_dir_type >> *(base_parser.white_space >> base_parser.sweep_param_value)] |
            hold[base_parser.step_dir_type >> base_parser.restOfLine]
            ;

        //commands in TSPICE that are not in Xyce
        acmodel_dir_type =
            qi::as_string[no_case[lit(".acmodel")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        alter_dir_type =
            qi::as_string[no_case[lit(".alter")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        assert_dir_type =
            qi::as_string[no_case[lit(".assert")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        checkpoint_dir_type =
            qi::as_string[no_case[lit(".checkpoint")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        connect_dir_type =
            qi::as_string[no_case[lit(".connect")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        data_dir_type =
            qi::as_string[no_case[lit(".data")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        enddata_dir_type =
            qi::as_string[no_case[lit(".enddata")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        dellib_dir_type =
            qi::as_string[no_case[lit(".del lib")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;
        global_dir_type =
            qi::as_string[no_case[lit(".global")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        hdl_dir_type =
            qi::as_string[no_case[lit(".hdl")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        if_dir_type =
            qi::as_string[no_case[lit(".if")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        else_dir_type =
            qi::as_string[no_case[lit(".else")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        elseif_dir_type =
            qi::as_string[no_case[lit(".elseif")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        endif_dir_type =
            qi::as_string[no_case[lit(".endif")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        load_dir_type =
            qi::as_string[no_case[lit(".load")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        malias_dir_type =
            qi::as_string[no_case[lit(".malias")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        optgoal_dir_type =
            qi::as_string[no_case[lit(".optgoal")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        optimize_dir_type =
            qi::as_string[no_case[lit(".optimize")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        paramlimits_dir_type =
            qi::as_string[no_case[lit(".paramlimits")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        power_dir_type =
            qi::as_string[no_case[lit(".power")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        probe_dir_type =
            qi::as_string[no_case[lit(".probe")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        protect_dir_type =
            qi::as_string[no_case[lit(".protect")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        unprotect_dir_type =
            qi::as_string[no_case[lit(".unprotect")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        savebias_dir_type =
            qi::as_string[no_case[lit(".savebias")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        temp_dir_type =
            qi::as_string[no_case[lit(".temp")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        tf_dir_type =
            qi::as_string[no_case[lit(".tf")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        vector_dir_type =
            qi::as_string[no_case[lit(".vector")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        warn_dir_type =
            qi::as_string[no_case[lit(".warn")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        gridsize_dir_type =
            qi::as_string[no_case[lit(".gridsize")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        table_dir_type =
            qi::as_string[no_case[lit(".table")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        vrange_dir_type =
            qi::as_string[no_case[lit(".vrange")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;


        //unsupported and unresolvable commands
        acmodel_dir =
            acmodel_dir_type >> base_parser.restOfLine
            ;

        data_dir =
            data_dir_type >> base_parser.restOfLine
            ;

        enddata_dir =
            enddata_dir_type >> base_parser.restOfLine
            ;

        dellib_dir =
            dellib_dir_type >> base_parser.restOfLine
            ;

        hdl_dir =
            hdl_dir_type >> base_parser.restOfLine
            ;

        if_dir =
            if_dir_type >> base_parser.restOfLine
            ;

        elseif_dir =
            elseif_dir_type >> base_parser.restOfLine
            ;

        else_dir =
            else_dir_type >> base_parser.restOfLine
            ;

        endif_dir =
            endif_dir_type >> base_parser.restOfLine
            ;

        optimize_dir =
            optimize_dir_type >> base_parser.restOfLine
            ;

        optgoal_dir =
            optgoal_dir_type >> base_parser.restOfLine
            ;

        protect_dir =
            protect_dir_type >> base_parser.restOfLine
            ;

        unprotect_dir =
            unprotect_dir_type >> base_parser.restOfLine
            ;

        tf_dir =
            tf_dir_type >> base_parser.restOfLine
            ;

        vector_dir =
            vector_dir_type >> base_parser.restOfLine
            ;

        warn_dir =
            warn_dir_type >> base_parser.restOfLine
            ;

        gridsize_dir =
            gridsize_dir_type >> base_parser.restOfLine
            ;

        table_dir =
            table_dir_type >> base_parser.restOfLine
            ;

        vrange_dir =
            vrange_dir_type >> base_parser.restOfLine
            ;

        //unsupported but could possibly be resolved commands
        alter_dir =
            alter_dir_type >> base_parser.restOfLine
            ;//copy all previous code with changes and run again

        assert_dir =
            assert_dir_type >> base_parser.restOfLine
            ;//try and do same/similar thing using .options

        checkpoint_dir =
            checkpoint_dir_type >> base_parser.restOfLine
            ;//try and use .options restart

        connect_dir =
            connect_dir_type >> base_parser.restOfLine
            ;//go through all code and replace node2 with node1

        global_dir =
            global_dir_type >> base_parser.restOfLine
            ;//change node name(s) to $Gname

        lib_dir =
            base_parser.lib_dir_type >>  base_parser.white_space >> base_parser.filename
            ;

        load_dir =
            load_dir_type >> base_parser.restOfLine
            ;//put code from file into netlist inplace of load line

        malias_dir =
            malias_dir_type >> base_parser.restOfLine
            ;//add alias directory? change names?

        power_dir =
            power_dir_type >> base_parser.restOfLine
            ;//if no A and Z specified do .print .tran P(source)

        probe_dir =
            probe_dir_type >> base_parser.restOfLine
            ;//basically print to a binary file?

        savebias_dir =
            savebias_dir_type >> base_parser.restOfLine
            ;//sort of like save with different parameters

        temp_dir =
            temp_dir_type >> base_parser.restOfLine
            ;//use global_param TEMP=value instead?


        //Devices that need to be overwritten
        current_ctrl_current_src =
            hold[base_parser.current_ctrl_current_src_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> base_parser.white_space >> base_parser.poly >> base_parser.white_space >> +(base_parser.control_param_value) >> +(base_parser.white_space >> base_parser.poly_param_value) >> *(base_parser.white_space >> base_parser.param_value_pair)] |
            hold[base_parser.current_ctrl_current_src_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> base_parser.white_space >> base_parser.control_param_value >> base_parser.white_space >> base_parser.GAIN_VALUE >> *(base_parser.param_value_pair)]
            ;

        current_ctrl_voltage_src =
            hold[base_parser.current_ctrl_voltage_src_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> base_parser.white_space >> base_parser.poly >> +(base_parser.control_param_value) >> +(base_parser.white_space >> base_parser.poly_param_value) >> *(base_parser.white_space >> base_parser.param_value_pair)] |
            hold[base_parser.current_ctrl_voltage_src_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> base_parser.white_space >> base_parser.control_param_value >> base_parser.white_space >> base_parser.GAIN_VALUE >> *(base_parser.param_value_pair)]
            ;

        inductor =
            hold[base_parser.inductor_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> *(base_parser.white_space >> !base_parser.param_value_pair >> base_parser.model_or_value) >> *(base_parser.white_space >> base_parser.param_value_pair)] |
            hold[base_parser.inductor_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> base_parser.poly >> base_parser.white_space >> +(base_parser.white_space >> base_parser.poly_param_value) >> *(base_parser.white_space >> base_parser.param_value_pair)]
            ;

        mesfet =
            base_parser.mesfet_type >> -base_parser.devname >> base_parser.white_space >> base_parser.DRAINNODE >> base_parser.white_space >> base_parser.GATENODE >> base_parser.white_space >> base_parser.SOURCENODE >> -(base_parser.white_space >> base_parser.SUBSTRATENODE) >> base_parser.white_space >> base_parser.model_name >> -(base_parser.white_space >> !base_parser.param_value_pair >> base_parser.param_value) >> *(base_parser.white_space >> base_parser.param_value_pair)
            ;

        resistor =
            base_parser.resistor_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> *(base_parser.white_space >> !base_parser.param_value_pair >> base_parser.model_or_value) >> *(base_parser.white_space >> base_parser.param_value_pair)
            ;

        current_ctrl_switch =
            base_parser.voltage_ctrl_switch_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSSWITCHNODE >> base_parser.white_space >> base_parser.NEGSWITCHNODE >> base_parser.white_space >> base_parser.control_param_value >> base_parser.white_space >> base_parser.model_name
            ;//TSPICE CCswitch has S heading just like VCswitch and no ON/OFF, how to handle?

        //Not Supported?
        lossy_trans_line =
            base_parser.lossless_trans_line_type >> base_parser.devname >> base_parser.white_space >> base_parser.APORTPOSNODE >> base_parser.white_space >> base_parser.APORTNEGNODE >> base_parser.white_space >> base_parser.BPORTPOSNODE >> base_parser.white_space >> base_parser.BPORTNEGNODE >> *(base_parser.white_space >> base_parser.param_value_pair)
            ;//TSPICE lossy trans lines have T heading but are otherwise the same except the variables that would be in a model in Xyce are in parameters in TSPICE
        //How to resolve parameter vs model difference

        voltage_ctrl_resistor =
            base_parser.voltage_ctrl_current_src_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> base_parser.white_space >> /*qi::as_string[no_case[lit("VCR")]] >>*/ base_parser.restOfLine
            ;//VCR unsupported by Xyce

        voltage_ctrl_current_src =
            hold[base_parser.voltage_ctrl_current_src_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> base_parser.white_space >> base_parser.poly >> +(base_parser.white_space >> base_parser.POSCONTROLNODE >> base_parser.white_space >> base_parser.NEGCONTROLNODE) >> +(base_parser.white_space >> base_parser.poly_param_value) >> *(base_parser.white_space >> base_parser.param_value_pair)] |
            hold[base_parser.voltage_ctrl_current_src_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> base_parser.white_space >> base_parser.POSCONTROLNODE >> base_parser.white_space >> base_parser.NEGCONTROLNODE >> base_parser.white_space >> base_parser.TRANSCONDUCTANCE_VALUE >> *(base_parser.white_space >> base_parser.param_value_pair)] |
            hold[base_parser.voltage_ctrl_current_src_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> base_parser.white_space >> /*qi::as_string[no_case[lit("PWL")]] >>*/ base_parser.restOfLine] |
            hold[base_parser.voltage_ctrl_current_src_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> base_parser.white_space >> /*qi::as_string[no_case[lit("LAPLACE")]] >>*/ base_parser.restOfLine] |
            hold[base_parser.voltage_ctrl_current_src_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> *(base_parser.white_space >> base_parser.value_expression) >> *(base_parser.white_space >> base_parser.param_value_pair)]
            ;//Xyce does not support PWL or LAPLACE for VCCS

        voltage_ctrl_voltage_src =
            hold[base_parser.voltage_ctrl_voltage_src_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> base_parser.white_space >> base_parser.poly >> +(base_parser.white_space >> base_parser.POSCONTROLNODE >> base_parser.white_space >> base_parser.NEGCONTROLNODE) >> +(base_parser.white_space >> base_parser.poly_param_value) >> *(base_parser.white_space >> base_parser.param_value_pair)] |
            hold[base_parser.voltage_ctrl_voltage_src_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> base_parser.white_space >> base_parser.POSCONTROLNODE >> base_parser.white_space >> base_parser.NEGCONTROLNODE >> base_parser.white_space >> base_parser.GAIN_VALUE >> *(base_parser.white_space >> base_parser.param_value_pair)] |
            hold[base_parser.voltage_ctrl_voltage_src_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> base_parser.white_space >> /*qi::as_string[no_case[lit("LAPLACE")]] >>*/ base_parser.restOfLine] |
            hold[base_parser.voltage_ctrl_voltage_src_dev_type >> -base_parser.devname >> base_parser.white_space >> base_parser.POSNODE >> base_parser.white_space >> base_parser.NEGNODE >> base_parser.white_space >> base_parser.value_expression >> *(base_parser.white_space >> base_parser.param_value_pair)]
            ;//Xyce does not support LAPLACE for VCVS*/

    }

    };
#endif
