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


#if !defined(BOOST_SPIRIT_SPECTRE)
#define BOOST_SPIRIT_SPECTRE

#include "boost_adm_parser_common.h"
#include <string>
#include <unordered_map>

namespace qi = boost::spirit::qi;
namespace ascii = boost::spirit::ascii;

using namespace adm_boost_common;

template <typename Iterator>
struct spectre_parser : qi::grammar<Iterator, std::vector<netlist_statement_object>()>
{

    qi::rule<Iterator, std::vector<netlist_statement_object>()>
        spectre_line, ac_param_value_pair, param_value_pair, directive
        ;

    qi::rule<Iterator, std::vector<netlist_statement_object>()>
        bsource, capacitor, device, diode, inductor, mutual_inductor, port, resistor, mesfet,
        lossless_trans_line, jfet, gain, cccs, vcvs, vccs, pvcvs, pvccs, vsource, isource,
        unknown_device, model_dir, param_dir, subckt_dir, ends_dir, func_dir, func_expr_dir, include_dir,
        library_dir, endlibrary_dir, modelParameter_dir, section_dir, endsection_dir,
        ac_dir, binned_model_dir, dc_dir, global_dir, tran_dir, save_dir, savestate_dir, sens_dir, if_dir,
        else_dir, else_if_dir, spectrerf_dir, stitch_dir, vector_dir, veriloga_dir, simulator_dir,
        unsupported_dir, delimiter_open_dir, delimiter_close_dir, source_inst_params,
        mutual_inductor_inst_params, port_inst_params, dc_inst_params
            ;

    qi::rule<Iterator, netlist_statement_object()>
        COUPLING_VALUE, GAIN_VALUE, POSNODE, NEGNODE, POSCONTROLNODE, NEGCONTROLNODE, DRAINNODE,
        GATENODE, SOURCENODE, APORTPOSNODE, APORTNEGNODE, BPORTPOSNODE, BPORTNEGNODE,
        UNKNOWN_NODE, ac_mag_value, ac_phase_value, control_inductor_dev_name,
        control_inductor_dev_type, dc_value_type, dc_value_value, output_variable, general_node,
        comment, inline_comment, binned_model_name, devname, model_dir_type, model_name, model_type,
        param_dir_type, ends_dir_type, func_dir_type, delimiter_open_dir_type,
        delimiter_close_dir_type, capacitor_dev_type, diode_dev_type, inductor_dev_type, mutual_inductor_dev_type,
        resistor_dev_type, subckt_dir_type, param_name, wave_param_name, param_value,
        subckt_directive_param_value, transient_ref_name, params_set_type, port_type,
        mesfet_type, lossless_trans_line_type, jfet_type, cccs_type, vcvs_type, vccs_type,
        pvcvs_type, pvccs_type, vsource_type, isource_type, include_type,
        library_type, endlibrary_type, section_type, modelParameter_type,
        endsection_type, filename, lib_entry, restOfLine, ac_dir_type,
        alter_dir_type, altergroup_dir_type, check_dir_type, checklimit_dir_type,
        cosim_dir_type, dc_dir_type, dcmatch_dir_type, envlp_dir_type, hb_dir_type,
        hbac_dir_type, hbnoise_dir_type, hbsp_dir_type, info_dir_type,
        loadpull_dir_type, montecarlo_dir_type, noise_dir_type, options_dir_type,
        pac_dir_type, pdisto_dir_type, pnoise_dir_type, psp_dir_type, pss_dir_type,
        pstb_dir_type, pxf_dir_type, pz_dir_type, qpac_dir_type, qpnoise_dir_type,
        qpsp_dir_type, qpss_dir_type, qpxf_dir_type, reliability_dir_type,
        set_dir_type, shell_dir_type, sp_dir_type, stb_dir_type, sweep_dir_type,
        tdr_dir_type, tran_dir_type, uti_dir_type, xf_dir_type,
        analogmodel_dir_type, bsource_dir_type, checkpoint_dir_type,
        smiconfig_dir_type, constants_dir_type, convergence_dir_type,
        encryption_dir_type, expressions_dir_type, else_dir_type, else_if_dir_type,
        functions_dir_type, global_dir_type, ibis_dir_type, ic_dir_type, if_dir_type,
        keywords_dir_type, memory_dir_type, nodeset_dir_type,
        param_limits_dir_type, paramset_dir_type, rfmemory_dir_type, save_dir_type,
        savestate_dir_type, sens_dir_type, spectrerf_dir_type, stitch_dir_type,
        vector_dir_type, veriloga_dir_type, simulator_dir_type,
        simulator_options_dir_type, finalTimeOP_dir_type, element_dir_type,
        outputParameter_dir_type, designParamVals_dir_type, primitives_dir_type,
        subckts_dir_type, saveOptions_dir_type, line_fragment, lin_sweep_type, dec_sweep_type,
        points_value, start_freq_value, end_freq_value, current_type, voltage_type, 
        FUNC_ARG_VALUE, FUNC_NAME_VALUE, FUNC_EXPRESSION, IF_COND, abm_expression,
        dc_sweep_dev, dc_sweep_param, dc_sweep_start, dc_sweep_stop, dc_sweep_step
            ;

    qi::rule<Iterator, std::string()>
        control_inductor_identifier, identifier, raw_identifier, math_expression,
        undelimited_math_expression, comment_str, inline_comment_str, bracket_param,
        filename_str, any, line_fragment_str, math_operator, math_identifier, math_group,
        math_expression_in_group, binned_model_identifier
            ;

    qi::rule<Iterator> white_space, analysis_identifier;

    // part of an attempt to extract some common features between parsers into
    // a base parser, but it fails to compile

    // base_grammar<iterator_type> bp;

    spectre_parser() : spectre_parser::base_type(spectre_line)
    {
        using qi::lit;
        using qi::char_;
        using qi::lexeme;
        using qi::hold;
        using ascii::alnum;
        using ascii::string;
        using ascii::no_case;
        using namespace qi::labels;
        //using namespace boost::spirit; // This line causes ambiguous qi namespace definitions when built for linux / OSX (gcc or clang)

        // CORE TERMINALS

        any =
            *(char_)
            ;

        control_inductor_identifier =
            char_("i") >> char_("n") >> char_("d") >> +char_("0-9")
            ;

        identifier =
            raw_identifier >> *(hold[char_(":") >> raw_identifier])
            ;

        raw_identifier =
            +(hold[!(char_("/") >> char_("/"))] >> ~char_(":;(){}[],= \t"))
            ;

        binned_model_identifier =
            +char_("0-9")
            ;

        math_expression =
            //hold[char_("{") >> +char_("a-zA-Z0-9.+-/*(),_=<> \t!|$&:") >> char_("}")]
            +(hold[!(char_("/") >> char_("/"))] >> char_("_a-zA-Z0-9.+-/*(),=<>?:|&"))
            ;

        math_expression_in_group =
            +hold[char_("a-zA-Z0-9.+-/*,_=<> \t!|$&?:")]
            ;

        math_group =
            hold[-char_("+-") >> -white_space >> char_("(") >> +(math_group | math_expression_in_group) >> char_(")")]
            ;

        math_identifier =
            hold[!(char_("/") >> char_("/")) >> math_group] |
            hold[!(char_("/") >> char_("/")) >> -(char_("+-") >> -white_space) >> +char_("_a-zA-Z0-9.") >> -white_space >> math_group] |
            hold[!(char_("/") >> char_("/")) >> -(char_("+-") >> -white_space) >> +char_("_a-zA-Z0-9.")]
            ;

        math_operator =
            hold[!(char_("/") >> char_("/"))] >> +char_("+-/*,!=<>?:|&")
            ;

        undelimited_math_expression =
            +hold[math_identifier >> -hold[(-white_space >> !(char_("/") >> char_("/")) >> math_operator >> -white_space)]] >> -(-white_space >> lit(";"))
            ;

        output_variable =
            (identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::OUTPUT_VARIABLE))]
            ;

        inline_comment_str =
            char_("/") >> char_("/") >> *(char_);
        ;

        comment_str =
            ("//" >> *(char_)) | (char_("*") >> *(char_));
        ;

        line_fragment_str =
            +(!(char_("/") >> char_("/")) >> (char_))
        ;

        white_space = +char_(" \t");

        analysis_identifier =
            +(~char_("$:;(){}[],= \t'"))
            ;

        inline_comment =
            inline_comment_str [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::INLINE_COMMENT))]
            ;

        comment =
            comment_str [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::COMMENT))]
            ;

        line_fragment =
            line_fragment_str [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::REST_OF_LINE))]
            ;

        FUNC_EXPRESSION =
            undelimited_math_expression [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::FUNC_EXPRESSION))]
            ;

        IF_COND =
            undelimited_math_expression [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::CONDITIONAL_STATEMENT))]
            ;

        
        binned_model_name =
            binned_model_identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::BINNED_MODEL_NAME))]
            ;

        devname =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_NAME))]
            ;

        device =
            (bsource | capacitor | resistor | inductor | mutual_inductor | diode |
             mesfet | jfet | lossless_trans_line | vcvs | vccs | port | pvcvs |
             pvccs | vsource | isource | unknown_device)
            //            unknown_device
            ;


        restOfLine =
            any [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::REST_OF_LINE))]
            ;

        bracket_param =
            hold[char_("[") >>
            +(-(+char_(" ")) >> +(!(char_("/") >> char_("/")) >> char_("_a-zA-Z0-9.+-/*()"))) >>
            char_("]")]
            ;

        param_name =
            identifier
            [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::PARAM_NAME))]
            ;

        wave_param_name =
            qi::as_string[no_case[lit("wave")]]
            [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::PARAM_NAME))]
            ;

        param_value =
            (bracket_param | undelimited_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::PARAM_VALUE))]
            ;

        ac_param_value_pair =
            hold[(dec_sweep_type | lin_sweep_type) >> -white_space >> lit("=") >> -white_space >> points_value] |
            hold[lit("start") >> -white_space >> lit("=") >> -white_space >> start_freq_value] |
            hold[lit("stop") >> -white_space >> lit("=") >> -white_space >> end_freq_value]
            ;

        general_node =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::GENERALNODE))]
            ;

        param_value_pair =
            hold[wave_param_name >> lit("=") >> -white_space >> lit("[") >> +(-white_space >>
                    transient_ref_name) >> -white_space >> lit("]")]  |
            hold[param_name >> -white_space >> !inline_comment >> lit("=")
            >> -white_space >> param_value >> lit(",") >> param_value] |
            hold[param_name >> -white_space >> !inline_comment >> lit("=")
            >> -white_space >> param_value]
            ;

        transient_ref_name =
            (undelimited_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::TRANS_REF_NAME))]
            ;

        COUPLING_VALUE =
            (identifier | undelimited_math_expression) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::COUPLING_VALUE))]
            ;

        FUNC_ARG_VALUE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::FUNC_ARG_VALUE))]
            ;

        FUNC_NAME_VALUE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::FUNC_NAME_VALUE))]
            ;

        GAIN_VALUE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::GAIN_VALUE))]
            ;

        POSNODE =
            identifier [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::POSNODE))]
            ;

        NEGNODE =
            identifier [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::NEGNODE))]
            ;

        POSCONTROLNODE =
            identifier [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::POSCONTROLNODE))]
            ;

        NEGCONTROLNODE =
            identifier [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::NEGCONTROLNODE))]
            ;

        DRAINNODE =
            identifier [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::DRAINNODE))]
            ;

        GATENODE =
            identifier [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::GATENODE))]
            ;

        SOURCENODE =
            identifier [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::SOURCENODE))]
            ;

        APORTPOSNODE =
            identifier [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::APORTPOSNODE))]
            ;

        APORTNEGNODE =
            identifier [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::APORTNEGNODE))]
            ;

        BPORTPOSNODE =
            identifier [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::BPORTPOSNODE))]
            ;

        BPORTNEGNODE =
            identifier [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::BPORTNEGNODE))]
            ;

        UNKNOWN_NODE =
            identifier [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::UNKNOWN_NODE))]
            ;

        abm_expression =
            undelimited_math_expression [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::EXPRESSION))]
            ;

        dc_value_value =
            (math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DC_VALUE_VALUE))]
            ;

        ac_mag_value =
            (math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::AC_MAG_VALUE))]
            ;

        ac_phase_value =
            (math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::AC_PHASE_VALUE))]
            ;

        control_inductor_dev_name =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::CONTROL_DEVICE_NAME))]
            ;

        current_type =
            qi::as_string[lit("i")] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::CURRENT))]
            ;

        voltage_type =
            qi::as_string[lit("v")] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::VOLTAGE))]
            ;

        dec_sweep_type =
            qi::as_string[no_case[lit("DEC")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::SWEEP_TYPE))]
            ;

        lin_sweep_type =
            qi::as_string[no_case[lit("LIN")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::SWEEP_TYPE))]
            ;

        dc_sweep_dev =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DC_SWEEP_DEV))]
            ;

        dc_sweep_param =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DC_SWEEP_PARAM))]
            ;

        dc_sweep_start =
            (math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DC_SWEEP_START))]
            ;

        dc_sweep_stop =
            (math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DC_SWEEP_STOP))]
            ;

        dc_sweep_step =
            (math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DC_SWEEP_STEP))]
            ;

        model_name =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::MODEL_NAME))]
            ;

        model_type =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::MODEL_TYPE))]
            ;

        points_value =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::POINTS_VALUE))]
            ;

        start_freq_value =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::START_FREQ_VALUE))]
            ;

        end_freq_value =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::END_FREQ_VALUE))]
            ;

        subckt_dir_type =
            -(lit("inline") >> white_space) >> qi::as_string[no_case[lit("subckt")]]
            [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        // subckt_dir = (
        //     hold[subckt_dir_type
        //         >> white_space
        //         >> devname
        //         >> +(white_space >> !param_value_pair >> subckt_directive_param_value)
        //         >> *(white_space >> param_value_pair)] |
        //     hold[subckt_dir_type
        //         >> white_space
        //         >> devname >> -white_space >> "("
        //         >> +(white_space >> !param_value_pair >> subckt_directive_param_value)
        //         >> *(white_space >> param_value_pair) >> -white_space >> ")"] |
        //     hold[subckt_dir_type
        //         >> white_space
        //         >> devname
        //         >> +(white_space >> !params_set_type >> subckt_directive_param_value)
        //         >> -(white_space >> params_set_type >> +(white_space >> param_value_pair))] |
        //     hold[subckt_dir_type
        //         >> white_space
        //         >> devname >> -white_space >> "("
        //         >> +(white_space >> !params_set_type >> subckt_directive_param_value)
        //         >> -(white_space >> params_set_type >> +(white_space >> param_value_pair)) >> ")"]
        //     )
        // ;

        subckt_dir =
            subckt_dir_type
            >> white_space
            >> devname >> white_space >> -lit("(")
            >> +(-white_space >> subckt_directive_param_value) >> -white_space >> -lit(")")
            >> -(white_space >> params_set_type >> +(white_space >> param_value_pair))
            ;


        subckt_directive_param_value =
            (identifier)
            [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::SUBCKT_DIRECTIVE_PARAM_VALUE))]
            ;

        params_set_type =
            qi::as_string[no_case[lit("parameters")]]
            [symbol_adder(
                    _val,
                    std::string("PARAMS:"),
                    vector_of<data_model_type>(adm_boost_common::PARAMS_HEADER))]
            ;

        ends_dir_type =
            qi::as_string[no_case[lit("ends")]]
            [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        ends_dir =
            ends_dir_type >> -(white_space >> param_value)
            ;

        include_type =
            qi::as_string[no_case[lit("include")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        filename_str =
            -char_("\"") >> +char_("a-zA-Z0-9.\\/:_-") >> -char_("\"");
            ;

        filename =
            filename_str [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::FILENAME))]
            ;

        lib_entry =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::LIB_ENTRY))]
            ;

        include_dir =
            include_type >> white_space >> -lit("\"") >> filename >> -lit("\"") >> -(white_space >> lit("section=") >>
                    -white_space >> lib_entry);
        ;

        library_type =
            qi::as_string[no_case[lit("library")]]
            [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        library_dir =
            library_type >> restOfLine
            ;

        section_type =
            qi::as_string[no_case[lit("section")]]
            [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        section_dir =
            section_type >> white_space >> lib_entry >> -(white_space >> restOfLine);
        ;

        modelParameter_type =
            qi::as_string[no_case[lit("modelParameter")]]
            [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        modelParameter_dir =
            modelParameter_type >> restOfLine;
        ;

        endsection_type =
            qi::as_string[no_case[lit("endsection")]]
            [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        endsection_dir =
            endsection_type >> -(white_space >> lib_entry)
            ;


        endlibrary_type =
            qi::as_string[no_case[lit("endlibrary")]]
            [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        endlibrary_dir =
            endlibrary_type >> restOfLine
            ;

        // UNSUPPORTED COMMANDS

        alter_dir_type =
            qi::as_string[no_case[lit("alter")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        altergroup_dir_type =
            qi::as_string[no_case[lit("altergroup")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        check_dir_type =
            qi::as_string[no_case[lit("check")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        checklimit_dir_type =
            qi::as_string[no_case[lit("checklimit")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        cosim_dir_type =
            qi::as_string[no_case[lit("cosim")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        dcmatch_dir_type =
            qi::as_string[no_case[lit("dcmatch")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        envlp_dir_type =
            qi::as_string[no_case[lit("envlp")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        hb_dir_type =
            qi::as_string[no_case[lit("hb")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        hbac_dir_type =
            qi::as_string[no_case[lit("hbac")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        hbnoise_dir_type =
            qi::as_string[no_case[lit("hbnoise")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        hbsp_dir_type =
            qi::as_string[no_case[lit("hbsp")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        info_dir_type =
            qi::as_string[no_case[lit("info")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        loadpull_dir_type =
            qi::as_string[no_case[lit("loadpull")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        montecarlo_dir_type =
            qi::as_string[no_case[lit("montecarlo")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        noise_dir_type =
            qi::as_string[no_case[lit("noise")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        options_dir_type =
            qi::as_string[no_case[lit("options")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        pac_dir_type =
            qi::as_string[no_case[lit("pac")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        pdisto_dir_type =
            qi::as_string[no_case[lit("pdisto")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        pnoise_dir_type =
            qi::as_string[no_case[lit("pnoise")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        psp_dir_type =
            qi::as_string[no_case[lit("psp")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        pss_dir_type =
            qi::as_string[no_case[lit("pss")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        pstb_dir_type =
            qi::as_string[no_case[lit("pstb")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        pxf_dir_type =
            qi::as_string[no_case[lit("pxf")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        pz_dir_type =
            qi::as_string[no_case[lit("pz")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        qpac_dir_type =
            qi::as_string[no_case[lit("qpac")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        qpnoise_dir_type =
            qi::as_string[no_case[lit("qpnoise")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        qpsp_dir_type =
            qi::as_string[no_case[lit("qpsp")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        qpss_dir_type =
            qi::as_string[no_case[lit("qpss")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        qpxf_dir_type =
            qi::as_string[no_case[lit("qpxf")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        reliability_dir_type =
            qi::as_string[no_case[lit("reliability")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        set_dir_type =
            qi::as_string[no_case[lit("set")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        shell_dir_type =
            qi::as_string[no_case[lit("shell")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        sp_dir_type =
            qi::as_string[no_case[lit("sp")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        stb_dir_type =
            qi::as_string[no_case[lit("stb")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        sweep_dir_type =
            qi::as_string[no_case[lit("sweep")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        tdr_dir_type =
            qi::as_string[no_case[lit("tdr")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        uti_dir_type =
            qi::as_string[no_case[lit("uti")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        xf_dir_type =
            qi::as_string[no_case[lit("xf")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        analogmodel_dir_type =
            qi::as_string[no_case[lit("analogmodel")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        checkpoint_dir_type =
            qi::as_string[no_case[lit("checkpoint")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        smiconfig_dir_type =
            qi::as_string[no_case[lit("smiconfig")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        constants_dir_type =
            qi::as_string[no_case[lit("constants")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        convergence_dir_type =
            qi::as_string[no_case[lit("convergence")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        else_dir_type =
            qi::as_string[no_case[lit("else")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        else_if_dir_type =
            qi::as_string[no_case[lit("else if")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        encryption_dir_type =
            qi::as_string[no_case[lit("encryption")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        expressions_dir_type =
            qi::as_string[no_case[lit("expressions")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        functions_dir_type =
            qi::as_string[no_case[lit("functions")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        ibis_dir_type =
            qi::as_string[no_case[lit("ibis")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        ic_dir_type =
            qi::as_string[no_case[lit("ic")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        if_dir_type =
            qi::as_string[no_case[lit("if")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        keywords_dir_type =
            qi::as_string[no_case[lit("keywords")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        memory_dir_type =
            qi::as_string[no_case[lit("memory")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        nodeset_dir_type =
            qi::as_string[no_case[lit("nodeset")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        param_limits_dir_type =
            qi::as_string[no_case[lit("param_limits")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        paramset_dir_type =
            qi::as_string[no_case[lit("paramset")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        rfmemory_dir_type =
            qi::as_string[no_case[lit("rfmemory")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        save_dir_type =
            qi::as_string[no_case[lit("save")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        savestate_dir_type =
            qi::as_string[no_case[lit("savestate")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        sens_dir_type =
            qi::as_string[no_case[lit("sens")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        spectrerf_dir_type =
            qi::as_string[no_case[lit("spectrerf")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        stitch_dir_type =
            qi::as_string[no_case[lit("stitch")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        vector_dir_type =
            qi::as_string[no_case[lit("vector")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        veriloga_dir_type =
            qi::as_string[no_case[lit("veriloga")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        simulator_dir_type =
            qi::as_string[no_case[lit("simulator")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        simulator_options_dir_type =
            qi::as_string[no_case[lit("simulatorOptions")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        finalTimeOP_dir_type =
            qi::as_string[no_case[lit("finalTimeOP")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        element_dir_type =
            qi::as_string[no_case[lit("element")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        outputParameter_dir_type =
            qi::as_string[no_case[lit("outputParameter")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        designParamVals_dir_type =
            qi::as_string[no_case[lit("designParamVals")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        primitives_dir_type =
            qi::as_string[no_case[lit("primitives")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        subckts_dir_type =
            qi::as_string[no_case[lit("subckts")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        saveOptions_dir_type =
            qi::as_string[no_case[lit("saveOptions")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        save_dir =
            save_dir_type >>
            !identifier >> // handles saveOptions conflict
            *(white_space >> output_variable)
            ;

        simulator_dir =
            simulator_dir_type >> white_space >> param_value_pair;
        ;



        unsupported_dir =
            (
             alter_dir_type |
             altergroup_dir_type |
             check_dir_type |
             checklimit_dir_type |
             cosim_dir_type |
             dcmatch_dir_type |
             envlp_dir_type |
             hb_dir_type |
             hbac_dir_type |
             hbnoise_dir_type |
             hbsp_dir_type |
             info_dir_type |
             loadpull_dir_type |
             montecarlo_dir_type |
             noise_dir_type |
             options_dir_type |
             pac_dir_type |
             pdisto_dir_type |
             pnoise_dir_type |
             psp_dir_type |
             pss_dir_type |
             pstb_dir_type |
             pxf_dir_type |
             pz_dir_type |
             qpac_dir_type |
             qpnoise_dir_type |
             qpsp_dir_type |
             qpss_dir_type |
             qpxf_dir_type |
             reliability_dir_type |
             set_dir_type |
             shell_dir_type |
             sp_dir_type |
             stb_dir_type |
             sweep_dir_type |
             tdr_dir_type |
             uti_dir_type |
             xf_dir_type |
             analogmodel_dir_type |
             checkpoint_dir_type |
             smiconfig_dir_type |
             constants_dir_type |
             convergence_dir_type |
             encryption_dir_type |
             expressions_dir_type |
             functions_dir_type |
             ibis_dir_type |
             ic_dir_type |
             keywords_dir_type |
             memory_dir_type |
             nodeset_dir_type |
             param_limits_dir_type |
             paramset_dir_type |
             rfmemory_dir_type |
             savestate_dir_type |
             sens_dir_type |
             spectrerf_dir_type |
             stitch_dir_type |
             vector_dir_type |
             veriloga_dir_type |
             simulator_options_dir_type |
             finalTimeOP_dir_type |
             element_dir_type |
             outputParameter_dir_type |
             designParamVals_dir_type |
             primitives_dir_type |
             subckts_dir_type |
             saveOptions_dir_type
             )
             >> restOfLine;
        ;

        // STARTING POINT ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        spectre_line = comment | hold[((directive | device) >> -(-white_space >> inline_comment))] | hold[(line_fragment >> -white_space >> inline_comment)]
            ;

        // DIRECTIVES ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////     ////////////////////////////////////////////////

        directive =
            (
             ac_dir | binned_model_dir | else_if_dir | else_dir | delimiter_open_dir | delimiter_close_dir |
             dc_dir | modelParameter_dir | section_dir | endsection_dir | func_dir | func_expr_dir | global_dir |
             model_dir | param_dir | ends_dir | if_dir | include_dir | library_dir | endlibrary_dir | tran_dir |
             save_dir | simulator_dir | subckt_dir | unsupported_dir
            )
            ;

        ac_dir_type =
            qi::as_string[no_case[lit("ac")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        ac_dir =
            hold[analysis_identifier >> white_space >> ac_dir_type >> white_space >> -(!ac_param_value_pair >> param_value_pair >> -white_space) >> 
            *(hold[ac_param_value_pair] >> -white_space >> -(!ac_param_value_pair >> hold[param_value_pair] >> -white_space))]
            ;

        binned_model_dir = 
            hold[binned_model_name >> -white_space >> lit(":") >> +(white_space >> param_value_pair)]
            ;

        dc_dir_type =
            qi::as_string[no_case[lit("dc")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        dc_inst_params =
            hold[white_space >> lit("dev") >> -white_space >> lit("=") >> -white_space >> dc_sweep_dev] |
            hold[white_space >> lit("param") >> -white_space >> lit("=") >> -white_space >> dc_sweep_param] |
            hold[white_space >> lit("start") >> -white_space >> lit("=") >> -white_space >> dc_sweep_start] |
            hold[white_space >> lit("stop") >> -white_space >> lit("=") >> -white_space >> dc_sweep_stop] |
            hold[white_space >> lit("step") >> -white_space >> lit("=") >> -white_space >> dc_sweep_step] |
            hold[white_space >> param_value_pair]
            ;

        dc_dir =
            hold[analysis_identifier >> white_space >> dc_dir_type >> +(dc_inst_params)]
            ;

        dc_value_type =
            qi::as_string[lit("dc")] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DC_VALUE))]
            ;

        delimiter_open_dir_type =
            qi::as_string[lit("{")][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::BLOCK_DELIMITER))]
            ;

        delimiter_open_dir =
            hold[delimiter_open_dir_type >> !(-white_space >> func_expr_dir)] 
            ;

        delimiter_close_dir_type =
            qi::as_string[lit("}")][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::BLOCK_DELIMITER))]
            ;

        delimiter_close_dir =
            hold[delimiter_close_dir_type >> qi::eol] |
            hold[delimiter_close_dir_type]
            ;


        else_dir =
            hold[delimiter_close_dir >> -white_space >> else_dir_type >> -(-white_space >> delimiter_open_dir)]
            ;


        else_if_dir =
            hold[delimiter_close_dir >> -white_space >> else_if_dir_type >> +(white_space >> IF_COND) >> -(-white_space >> delimiter_open_dir)]
            ;


        func_dir_type =
            qi::as_string[no_case[lit("real")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        func_dir =
            hold[func_dir_type >> white_space >> FUNC_NAME_VALUE >> -white_space >> lit("(") >> *hold[-white_space >> lit("real") >> white_space >> FUNC_ARG_VALUE >> -white_space >> lit(",")] >> -white_space >> lit("real") >> white_space >> FUNC_ARG_VALUE >> -white_space >> lit(")") >> -white_space >> delimiter_open_dir_type >> -white_space >> lit("return") >> white_space >> FUNC_EXPRESSION >> -white_space >> delimiter_close_dir] | 
            hold[func_dir_type >> white_space >> FUNC_NAME_VALUE >> -white_space >> lit("(") >> *hold[-white_space >> lit("real") >> white_space >> FUNC_ARG_VALUE >> -white_space >> lit(",")] >> -white_space >> lit("real") >> white_space >> FUNC_ARG_VALUE >> -white_space >> lit(")") >> -white_space >> delimiter_open_dir] | 
            hold[func_dir_type >> white_space >> FUNC_NAME_VALUE >> -white_space >> lit("(") >> *hold[-white_space >> lit("real") >> white_space >> FUNC_ARG_VALUE >> -white_space >> lit(",")] >> -white_space >> lit("real") >> white_space >> FUNC_ARG_VALUE >> -white_space >> lit(")")]
            ;

        func_expr_dir =
            hold[-(delimiter_open_dir_type >> -white_space) >> lit("return") >> white_space >> FUNC_EXPRESSION >> -(-white_space >> delimiter_close_dir)]
            ;

        global_dir_type =
            qi::as_string[no_case[lit("global")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        global_dir =
            global_dir_type >> *(white_space >> general_node)
            ;

        if_dir =
            hold[if_dir_type >> +(white_space >> IF_COND) >> -(-white_space >> delimiter_open_dir)]
            ;

        model_dir_type =
            qi::as_string[no_case[lit("model")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        model_dir =
            hold[model_dir_type >> white_space >> model_name >> white_space >> model_type >> -white_space >> delimiter_open_dir_type] |
            hold[model_dir_type >> white_space >> model_name >> white_space >> model_type >> *(white_space >> param_value_pair)]
            ;

        mutual_inductor_inst_params =
            hold[white_space >> control_inductor_dev_type >> -white_space >> lit("=") >> -white_space >> control_inductor_dev_name] |
            hold[white_space >> lit("coupling") >> -white_space >> lit("=") >> -white_space >> COUPLING_VALUE]
            ;

        param_dir_type =
            qi::as_string[no_case[lit("parameters")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        param_dir =
            param_dir_type >> +(white_space >> param_value_pair >> -lit(","))
            ;

        port_inst_params =
            hold[white_space >> param_value_pair]
            ;

        source_inst_params =
            hold[white_space >> lit("type") >> -white_space >> lit("=") >> -white_space >> dc_value_type] |
            hold[white_space >> lit("dc") >> -white_space >> lit("=") >> -white_space >> dc_value_value] |
            hold[white_space >> lit("mag") >> -white_space >> lit("=") >> -white_space >> ac_mag_value] |
            hold[white_space >> lit("phase") >> -white_space >> lit("=") >> -white_space >> ac_phase_value] |
            hold[white_space >> param_value_pair]
            ;

        tran_dir_type =
            qi::as_string[no_case[lit("tran")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(
                        adm_boost_common::DIRECTIVE_TYPE))]
            ;

        tran_dir =
            tran_dir_type >> white_space >> tran_dir_type >> *(white_space >> param_value_pair)
            ;

        // ANALOG DEVICES  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


        bsource_dir_type =
            qi::as_string[no_case[lit("bsource")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        bsource = 
            hold[devname >> -white_space >> lit("(") >> -white_space >> POSNODE >> white_space >> NEGNODE >> -white_space >> lit(")") >> white_space >> bsource_dir_type >> white_space >> current_type >> -white_space >> lit("=") >> -white_space >> abm_expression] | 
            hold[devname >> -white_space >> lit("(") >> -white_space >> POSNODE >> white_space >> NEGNODE >> -white_space >> lit(")") >> white_space >> bsource_dir_type >> white_space >> voltage_type >> -white_space >> lit("=") >> -white_space >> abm_expression] 
            ;

        capacitor_dev_type =
            qi::as_string[no_case[lit("capacitor")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        // For parsing a line like this:
        // C1 (cc out) capacitor c=1pf
        capacitor = 
            // name
            // optional parentheses around nodes
            hold[devname >> -white_space >> "(" >> -white_space >> POSNODE >> white_space >> NEGNODE >> -white_space >> ")" >> white_space >> capacitor_dev_type >> !identifier >> *(white_space >> param_value_pair)] |
            hold[devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> capacitor_dev_type >> !identifier >> *(white_space >> param_value_pair)]
            ;

        diode_dev_type =
            qi::as_string[no_case[lit("diode")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        diode =
            hold[devname >> -white_space >> "(" >> -white_space >> POSNODE >> white_space >> NEGNODE >> -white_space >> ")" >> white_space >> diode_dev_type >> !identifier >> *(white_space >> param_value_pair)] |
            hold[devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> diode_dev_type >> !identifier >> *(white_space >> param_value_pair)]
            ;

        inductor_dev_type =
            qi::as_string[no_case[lit("inductor")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        inductor =
            hold[devname >> -white_space >> "(" >> -white_space >> POSNODE >> white_space >> NEGNODE >> -white_space >> ")" >> white_space >> inductor_dev_type >> !identifier >> *(white_space >> param_value_pair)] |
            hold[devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> inductor_dev_type >> !identifier >> *(white_space >> param_value_pair)]
            ;

        isource_type =
            qi::as_string[no_case[lit("isource")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        isource =
            hold[devname >> -white_space >> "(" >> -white_space >> POSNODE >> white_space >> NEGNODE >> -white_space >> ")" >> white_space >> isource_type >> !identifier >> *source_inst_params] |
            hold[devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> isource_type >> !identifier >> *source_inst_params]
            ;

        jfet_type =
            qi::as_string[no_case[lit("jfet")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        jfet =
            hold[devname >> -white_space >> "(" >> -white_space >> DRAINNODE >> white_space >> GATENODE >> white_space >> SOURCENODE >> -white_space >> ")" >> white_space >> jfet_type >> !identifier >> *(white_space >> param_value_pair)] |
            hold[devname >> white_space >> DRAINNODE >> white_space >> GATENODE >> white_space >> SOURCENODE >> white_space >> jfet_type >> !identifier >> *(white_space >> param_value_pair)]
            ;

        lossless_trans_line_type =
            qi::as_string[no_case[lit("tline")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        lossless_trans_line =
            hold[devname >> -white_space >> "(" >> -white_space >> APORTPOSNODE >> white_space >> APORTNEGNODE >> white_space >> BPORTPOSNODE >> white_space >> BPORTNEGNODE >> -white_space >> ")" >> white_space >> lossless_trans_line_type >> !identifier >> *(white_space >> param_value_pair)] |
            hold[devname >> white_space >> APORTPOSNODE >> white_space >> APORTNEGNODE >> white_space >> BPORTPOSNODE >> white_space >> BPORTNEGNODE >> white_space >> lossless_trans_line_type >> !identifier >> *(white_space >> param_value_pair)]
            ;

        mesfet_type =
            qi::as_string[no_case[lit("gaas")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        mesfet =
            hold[devname >> white_space >> DRAINNODE >> white_space >> GATENODE >> white_space >> SOURCENODE >> white_space >> mesfet_type >> !identifier >> *(white_space >> param_value_pair)] |
            hold[devname >> -white_space >> "(" >> -white_space >> DRAINNODE >> white_space >> GATENODE >> white_space >> SOURCENODE >> -white_space >> ")" >> white_space >> mesfet_type >> !identifier >> *(white_space >> param_value_pair)]
            ;

        control_inductor_dev_type =
            control_inductor_identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::CONTROL_DEVICE))]
            ;

        mutual_inductor_dev_type =
            qi::as_string[no_case[lit("mutual_inductor")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        mutual_inductor =
            hold[devname >> white_space >> mutual_inductor_dev_type >> !identifier >> *(mutual_inductor_inst_params)]
            ;

        port_type =
            qi::as_string[no_case[lit("port")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        port =
            hold[devname >> -white_space >> "(" >> -white_space >> POSNODE >> white_space >> NEGNODE >> -white_space >> ")" >> white_space >> port_type >> !identifier >> *port_inst_params] 
            ;

        resistor_dev_type =
            // commented out very hacky solution to a parsing problem that arises
            // when models have names that start with a master keyword
            // qi::as_string[no_case[lit("resistor ")]]
            qi::as_string[no_case[lit("resistor")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        resistor =
            // commented out very hacky solution to a parsing problem that arises
            // when models have names that start with a master keyword
            // >> *(param_value_pair >> -white_space)
            hold[devname >> -white_space >> "(" >> -white_space >> POSNODE >> white_space >> NEGNODE >> -white_space >> ")" >> hold[white_space >> resistor_dev_type] >> !identifier >> hold[*(white_space >> param_value_pair)]] |
            hold[devname >> white_space >> POSNODE >> white_space >> NEGNODE >> hold[white_space >> resistor_dev_type] >> !identifier >> hold[*(white_space >> param_value_pair)]]
            ;

        vsource_type =
            qi::as_string[no_case[lit("vsource")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        vsource =
            hold[devname >> -white_space >> "(" >> -white_space >> POSNODE >> white_space >> NEGNODE >> -white_space >> ")" >> white_space >> vsource_type >> !identifier >> *source_inst_params] |
            hold[devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> vsource_type >> !identifier >> *source_inst_params]
            ;

        gain =
            hold[white_space >> lit("gain") >> -white_space >> lit("=") >> -white_space >> GAIN_VALUE]
            ;

        vcvs_type =
            qi::as_string[no_case[lit("vcvs")]][symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        vcvs =
            hold[devname >> white_space >> lit("(") >> -white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> POSCONTROLNODE >> white_space >> NEGCONTROLNODE >> -white_space >> lit(")") >> white_space >> vcvs_type >> !identifier >> *(!gain >> white_space >> param_value_pair) >> gain >> *(white_space >> param_value_pair)] |
            hold[devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> POSCONTROLNODE >> white_space >> NEGCONTROLNODE >> white_space >> vcvs_type >> !identifier >> *(!gain >> white_space >> param_value_pair) >> gain >> *(white_space >> param_value_pair)] 
            ;

        vccs_type =
            qi::as_string[no_case[lit("vccs")]]
            [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        vccs =
            hold[devname >>
            (hold[-white_space >> "(" >> -white_space >>
             POSNODE >> white_space >>
             NEGNODE >> white_space >>
             POSCONTROLNODE >> white_space >>
             NEGCONTROLNODE >> -white_space >> ")"] |
             hold[
             white_space >>
             POSNODE >> white_space >>
             NEGNODE >> white_space >>
             POSCONTROLNODE >> white_space >>
             NEGCONTROLNODE]) >> white_space >>
            vccs_type >> !identifier >>
            *(white_space >> param_value_pair)]
            ;

        pvcvs_type =
            qi::as_string[no_case[lit("pvcvs")]]
            [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;


        pvcvs =
            hold[devname >>
            (hold[-white_space >> "(" >> -white_space >>
             POSNODE >> white_space >>
             NEGNODE >> white_space >>
             POSCONTROLNODE >> white_space >>
             NEGCONTROLNODE >> -white_space >> ")"] |
             hold[
             white_space >>
             POSNODE >> white_space >>
             NEGNODE >> white_space >>
             POSCONTROLNODE >> white_space >>
             NEGCONTROLNODE]) >> white_space >>
            pvcvs_type >> !identifier >>
            *(white_space >> param_value_pair)]
            ;

        pvccs_type =
            qi::as_string[no_case[lit("pvccs")]]
            [symbol_adder(
                    _val,
                    boost::spirit::_1,
                    vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        pvccs =
            hold[devname >>
            (hold[-white_space >> "(" >> -white_space >>
             POSNODE >> white_space >>
             NEGNODE >> white_space >>
             POSCONTROLNODE >> white_space >>
             NEGCONTROLNODE >> -white_space >> ")"] |
             hold[
             white_space >>
             POSNODE >> white_space >>
             NEGNODE >> white_space >>
             POSCONTROLNODE >> white_space >>
             NEGCONTROLNODE]) >> white_space >>
            pvccs_type >> !identifier >>
            *(white_space >> param_value_pair)]
            ;

        // The ordering of these rules matter. The grammar must first check for the device instantiation with instance
        // parameters first before moving on to check the device instantiation without instance parameters.
        unknown_device =
            hold[!subckt_dir_type >> devname >> -white_space >> "(" >> -white_space >> +(UNKNOWN_NODE >> -white_space) >> ")" >> white_space >> model_name >> +(white_space >> param_value_pair)] |
            hold[!subckt_dir_type >> devname >> -white_space >> "(" >> -white_space >> +(UNKNOWN_NODE >> -white_space) >> ")" >> white_space >> model_name] |
            hold[!subckt_dir_type >> devname >> white_space >> +(hold[!(model_name >> white_space >> param_value_pair) >> UNKNOWN_NODE >> white_space]) >> model_name >> +(white_space >> param_value_pair)] |
            hold[!subckt_dir_type >> devname >> white_space >> +(hold[!(model_name >> qi::eol) >> UNKNOWN_NODE >> white_space]) >> model_name] 
            ;
    }
};

#endif

