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


#if !defined(BOOST_SPIRIT_XYCE)
#define BOOST_SPIRIT_XYCE

#include "boost_adm_parser_common.h"

namespace qi = boost::spirit::qi;
namespace ascii = boost::spirit::ascii;

using namespace adm_boost_common;

template <typename Iterator>
struct xyce_parser : qi::grammar<Iterator, std::vector<netlist_statement_object>()>
{
    //friend struct pspice_parser : qi::grammar<Iterator, std::vector<netlist_statement_object>()>;

    qi::rule<Iterator, std::vector<netlist_statement_object>()> netlist_line, analog_device, directive, transient, transient_or_ac_dc, table, abm_expression, control_expression, value_expression, param_value_pair, measure_param_value_pair,
        circuit_params, poly, pulse_trans, sin_trans, exp_trans, pwl_trans, sffm_trans,
        port_param_value_pair, port_param_double_value_pair, port_param_triple_value_pair, port_param_quad_value_pair, 
        port_param_quint_value_pair, port_param_sextuplet_value_pair,
        port_param_value_pair_last, port_param_double_value_pair_last, port_param_triple_value_pair_last, port_param_quad_value_pair_last, port_param_quint_value_pair_last, port_param_sextuplet_value_pair_last;

    qi::rule<Iterator, std::vector<netlist_statement_object>()> bjt, capacitor, current_ctrl_current_src, current_ctrl_switch, current_ctrl_voltage_src, digital_dev, diode, inductor, port, resistor, indep_current_src,
        indep_voltage_src, jfet, lossless_trans_line, mosfet, mututal_inductor, non_linear_dep_src, subcircuit, voltage_ctrl_current_src, voltage_ctrl_switch, voltage_ctrl_voltage_src, mesfet, lossy_trans_line,
        generic_switch;

    qi::rule<Iterator, std::vector<netlist_statement_object>()> ac_dir, dc_dir, dcvolt_dir, end_dir, ends_dir, endl_dir, global_param_dir, global_dir, hb_dir, ic_dir, inc_dir, lib_dir, measure_dir, model_dir, nodeset_dir,
        op_dir, options_dir, param_dir, preprocess_dir, print_dir, save_dir, sens_dir, step_dir, subckt_dir, tran_dir, four_dir, func_dir, mor_dir, mpde_dir, lin_dir;

    qi::rule<Iterator, netlist_statement_object()> AREA_VALUE, TRANSCONDUCTANCE_VALUE, COUPLING_VALUE, FUND_FREQ_VALUE, GAIN_VALUE,
        GENERAL_VALUE, CONTROL_DEV_VALUE, POSNODE, NEGNODE, DRAINNODE, GATENODE, SOURCENODE, ANODE, POSCONTROLNODE,
        NEGCONTROLNODE, COLLECTORNODE, BASENODE, EMITTERNODE, COLLECTORPRIMENODE, BASEPRIMENODE, EMITTERPRIMENODE, POSSWITCHNODE,
        NEGSWITCHNODE, APORTPOSNODE, APORTNEGNODE, BPORTPOSNODE, BPORTNEGNODE, SUBSTRATENODE, TEMPERATURENODE, LOWOUTPUTNODE, HIGHOUTPUTNODE,
        INPUTREFERENCENODE, INPUTNODE, OUTPUTNODE, ACCELERATIONNODE, VELOCITYNODE, POSITIONNODE, THERMALNODE,
        EXTERNALBODYCONTACTNODE, INTERNALBODYCONTACTNODE, devname, devtype, control_inductor_dev_name,
        control_inductor_dev_type, vbic_model_type, vbic_model_name, model_name, model_or_value, opt_pack_type_value,
        capacitor_dev_type, port_dev_type, resistor_dev_type, transient_func_type, transient_ref_name, indep_voltage_src_type, model_dir_type, print_dir_type, func_dir_type,
        param_name, param_value, output_variable, analysis_type, param_dir_type, preprocess_dir_type, expression, non_linear_dep_src_type,
        diode_dev_type, ends_dir_type, end_dir_type, endl_dir_type, sweep_func_type, dc_dir_type, general_node, model_or_value_or_node, bjt_dev_type, mosfet_type, options_dir_type,
        tran_dir_type, indep_current_src_type, op_dir_type, subcircuit_type, subckt_dir_type, params_set_type, inline_comment, comment,
        ac_dir_type, global_param_dir_type, global_dir_type, step_dir_type, inductor_dev_type, model_or_node, ic_dir_type, ic_dir_type_alt, dcvolt_dir_type, simple_v_output, mutual_inductor_dev_type,
        current_ctrl_switch_dev_type, voltage_ctrl_switch_dev_type, digital_dev_type, lossless_trans_line_type, table_type, poly_type, voltage_ctrl_voltage_src_dev_type,
        on_type, off_type, list_sweep_type, lin_sweep_type, oct_sweep_type, dec_sweep_type, voltage_type, current_type, value_type, voltage_ctrl_current_src_dev_type,
        jfet_dev_type, param_type, objfunc_type, save_dir_type, sens_dir_type, model_type, inc_dir_type, lib_dir_type, measure_dir_type, filename, value_or_node, list_param_value, printStepValue, finalTimeValue,
        startTimeValue, stepCeilingValue, current_ctrl_current_src_dev_type, current_ctrl_voltage_src_dev_type, mesfet_type, lossy_trans_line_type, lib_entry, dc_value_type, dc_value_value,
        ac_value_type, ac_mag_value, ac_phase_value, result_name_value, measurement_type, hb_dir_type, preprocess_keyword, generic_switch_dev_type, control_str, table_param_value, poly_param_value,
        control_param_value, subckt_directive_param_value, subckt_device_param_value, points_value, start_freq_value, end_freq_value, nodeset_dir_type, FREQ_VALUE, four_dir_type, FUNC_ARG_VALUE,
        FUNC_NAME_VALUE, FUNC_EXPRESSION, NOOP_VALUE, UIC_VALUE, schedule_param_value, SCHEDULE_TYPE, sweep_param_value, restOfLine, mor_dir_type, mpde_dir_type, no_curly_brace_expression_sym,
        pulse_trans_type, sin_trans_type, exp_trans_type, pwl_trans_type, sffm_trans_type, default_param_name, lin_dir_type, measurement_qualifier, measure_param_name, measure_param_value, 
        variable_expr_or_value, standalone_param;

    qi::rule<Iterator, std::string()> identifier, math_expression, composite_math_expression, output_variable_expression, simple_v_output_expression, inline_comment_str, comment_str, filename_str,
        param_with_comma, raw_identifier, no_curly_brace_expression, any, port_param;

    qi::rule<Iterator> white_space;

    xyce_parser() : xyce_parser::base_type(netlist_line)
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

        identifier =
            raw_identifier >> *(hold[char_(":") >> raw_identifier])
            ;

        raw_identifier =
            +(~char_(":;(){}[],= \t"))
            ;

        no_curly_brace_expression =
            +char_("a-zA-Z0-9.+-/*(),_=<> \t!|$&:~")
            ;

        math_expression =
            char_("{") >> +char_("a-zA-Z0-9.+-/*(),_=<> \t!|$&:~") >> char_("}")
            ;

        composite_math_expression =
            char_("{") >> +(composite_math_expression | +char_("a-zA-Z0-9.+-/*(),_=<> \t!|$&:~")) >> char_("}")
            ;

        simple_v_output_expression =
            no_case[char_("V")]  >> char_("(") >> identifier >> char_(")")
            ;

        output_variable_expression =
            hold[no_case[char_("V")] >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")] |
            hold[no_case[char_("V")] >> no_case[char_("M")] >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")] |
            hold[no_case[char_("V")] >> no_case[char_("R")] >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")] |
            hold[no_case[char_("V")] >> no_case[char_("I")] >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")] |
            hold[no_case[char_("V")] >> no_case[char_("P")] >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")] |
            hold[no_case[char_("V")] >> no_case[char_("D")] >> no_case[char_("B")] >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")] |
            hold[no_case[char_("I")] >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")]  |
            hold[no_case[char_("I")] >> no_case[char_("M")] >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")] |
            hold[no_case[char_("I")] >> no_case[char_("R")] >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")] |
            hold[no_case[char_("I")] >> no_case[char_("I")] >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")] |
            hold[no_case[char_("I")] >> no_case[char_("P")] >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")] |
            hold[no_case[char_("I")] >> no_case[char_("D")] >> no_case[char_("B")] >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")] |
            hold[no_case[char_("I")] >> +char_("0-9") >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")] |
            hold[no_case[char_("N")] >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")] |
            hold[no_case[char_("W")] >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")] |
            hold[no_case[char_("P")] >> char_("(") >> -white_space >> identifier >> -(-white_space >> char_(",") >> -white_space >> identifier) >> -white_space >> char_(")")] |
            hold[simple_v_output_expression]
            ;

        inline_comment_str =
            char_(";") >> *(char_);
        ;

        comment_str =
            //hold[char_("#") | char_("*")] >> *(char_); - This form breakes the Windows build for some reason - switched ot the below (Antonio consulted) - RRL 9/4/15
            (char_("#") >> *(char_)) | (char_("*") >> *(char_));
        ;

        white_space = +char_(" \t");

        filename_str =
            -char_("\"") >> +char_("a-zA-Z0-9.\\/:-_") >> -char_("\"");
        ;

        restOfLine =
            any [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::REST_OF_LINE))]
            ;

        // NETLIST TERMINALS

        control_str =
            qi::as_string[no_case[lit("control")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::CONTROL))]
            ;

        voltage_type =
            qi::as_string[no_case[lit("V")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::VOLTAGE))]
            ;

        current_type =
            qi::as_string[no_case[lit("I")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::CURRENT))]
            ;

        SCHEDULE_TYPE =
            qi::as_string[no_case[lit("SCHEDULE")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::SCHEDULE_TYPE))]
            ;

        NOOP_VALUE =
            qi::as_string[no_case[lit("NOOP")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::NOOP_VALUE))]
            ;

        UIC_VALUE =
            qi::as_string[no_case[lit("UIC")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::UIC_VALUE))]
            ;

        standalone_param =
            qi::as_string[no_case[lit("TNODEOUT")]] [symbol_adder(_val, boost::spirit::_1,vector_of<data_model_type>(adm_boost_common::STANDALONE_PARAM))]
            ;

        inline_comment =
            inline_comment_str [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::INLINE_COMMENT))]
            ;

        comment =
            comment_str [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::COMMENT))]
            ;

        filename =
            filename_str [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::FILENAME))]
            ;

        param_value_pair =
            hold[param_name >> -white_space >> lit("=") >> -white_space >> param_value]
            ;

        measure_param_value_pair =
            hold[measure_param_name >> -white_space >> lit("=") >> -white_space >> measure_param_value]
            ;

        port_param =
            no_case[lit("dc")] | no_case[lit("z0")] | no_case[lit("hbac")] | no_case[lit("ac")] | no_case[lit("port")] |
            no_case[lit("hb")] | no_case[lit("rdc")] | no_case[lit("rac")] | no_case[lit("rhbac")] | no_case[lit("rtran")] |
            no_case[lit("power")] | no_case[lit("emphasis_level")] | no_case[lit("dcd")] | no_case[lit("dcd_type")] |
            no_case[lit("pj")] | no_case[lit("pj_type")] | no_case[lit("ami_obj")] | no_case[lit("ami_param")]
            ;

        port_param_value_pair =
            hold[param_name >> -white_space >> -lit("=") >> -white_space >> param_value >> &(white_space >> port_param)] 
            ;

        port_param_value_pair_last =
            hold[param_name >> -white_space >> -lit("=") >> -white_space >> param_value]
            ;

        port_param_double_value_pair =
            hold[param_name >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit(",") >> -white_space >> param_value >> &(white_space >> port_param)]
            ;

        port_param_double_value_pair_last =
            hold[param_name >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit(",") >> -white_space >> param_value]
            ;

        port_param_triple_value_pair =
            hold[param_name >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit(",") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> &(white_space >> port_param)]
            ;

        port_param_triple_value_pair_last =
            hold[param_name >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit(",") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value]
            ;

        port_param_quad_value_pair =
            hold[param_name >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit(",") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> &(white_space >> port_param)]
            ;

        port_param_quad_value_pair_last =
            hold[param_name >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value]
            ;

        port_param_quint_value_pair =
            hold[param_name >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> &(white_space >> port_param)]
            ;

        port_param_quint_value_pair_last =
            hold[param_name >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value]
            ;

        port_param_sextuplet_value_pair =
            hold[param_name >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> &(white_space >> port_param)]
            ;

        port_param_sextuplet_value_pair_last =
            hold[param_name >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value >> -white_space >> -lit("=") >> -white_space >> param_value]
            ;

        param_with_comma =
            identifier >> *(hold[-white_space >> char_(',') >> -white_space >> identifier >> !(white_space >> lit("=")) >> !(lit("="))])
            ;

        param_name =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::PARAM_NAME))]
            ;

        default_param_name =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEFAULT_PARAM_NAME))]
            ;

        measure_param_name =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::MEASURE_PARAM_NAME))]
            ;

        param_value =
            (composite_math_expression | param_with_comma) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::PARAM_VALUE))]
            ;

        printStepValue =
            (composite_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::PRINT_STEP_VALUE))]
            ;

        finalTimeValue =
            (composite_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::FINAL_TIME_VALUE))]
            ;

        startTimeValue =
            (composite_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::START_TIME_VALUE))]
            ;

        stepCeilingValue =
            (composite_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::STEP_CEILING_VALUE))]
            ;

        sweep_param_value =
            (composite_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::SWEEP_PARAM_VALUE))]
            ;

        list_param_value =
            (composite_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::LIST_PARAM_VALUE))]
            ;

        table_param_value =
            (composite_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::TABLE_PARAM_VALUE))]
            ;

        measure_param_value =
            (math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::MEASURE_PARAM_VALUE))]
            ;

        poly_param_value =
            (composite_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::POLY_PARAM_VALUE))]
            ;

        control_param_value =
            (composite_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::CONTROL_PARAM_VALUE))]
            ;

        schedule_param_value =
            (composite_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::SCHEDULE_PARAM_VALUE))]
            ;

        subckt_directive_param_value =
            (composite_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::SUBCKT_DIRECTIVE_PARAM_VALUE))]
            ;

        subckt_device_param_value =
            (composite_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::SUBCKT_DEVICE_PARAM_VALUE))]
            ;

        FUNC_EXPRESSION =
            math_expression [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::FUNC_EXPRESSION))]
            ;

        devname =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_NAME))]
            ;

        devtype =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIG_DEV_TYPE))]
            ;

        control_inductor_dev_name =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::CONTROL_DEVICE_NAME))]
            ;

        model_name =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::MODEL_NAME))]
            ;

        vbic_model_type =
            qi::as_string[no_case[lit("VBIC")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::VBIC_MODEL))]
            ;

        vbic_model_name =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::VBIC_MODEL_NAME))]
            ;

        dc_value_type =
            qi::as_string[no_case[lit("DC")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DC_VALUE))]
            ;

        dc_value_value =
            (composite_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DC_VALUE_VALUE))]
            ;

        ac_value_type =
            qi::as_string[no_case[lit("AC")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::AC_VALUE))]
            ;

        ac_mag_value =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::AC_MAG_VALUE))]
            ;

        ac_phase_value =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::AC_PHASE_VALUE))]
            ;

        measurement_type =
            (qi::as_string[no_case[lit("AVG")]] |
             qi::as_string[no_case[lit("DERIV")]] |
             qi::as_string[no_case[lit("DERIVATIVE")]] |
             qi::as_string[no_case[lit("DUTY")]] |
             qi::as_string[no_case[lit("ERROR")]] |
             qi::as_string[no_case[lit("EQN")]] |
             qi::as_string[no_case[lit("FREQ")]] |
             qi::as_string[no_case[lit("FOUR")]] |
             qi::as_string[no_case[lit("INTEG")]] |
             qi::as_string[no_case[lit("MAX")]] |
             qi::as_string[no_case[lit("MIN")]] |
             qi::as_string[no_case[lit("OFF_TIME")]] |
             qi::as_string[no_case[lit("ON_TIME")]] |
             qi::as_string[no_case[lit("PARAM")]] |
             qi::as_string[no_case[lit("PP")]] |
             qi::as_string[no_case[lit("RMS")]] |
             qi::as_string[no_case[lit("TRIG")]]) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::ANALYSIS_TYPE))]
            ;

        measurement_qualifier =
            (qi::as_string[no_case[lit("AT")]] |
             qi::as_string[no_case[lit("FILE")]] |
             qi::as_string[no_case[lit("TARG")]] |
             qi::as_string[no_case[lit("WHEN")]])  [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::MEASURE_QUALIFIER))]
            ;

        result_name_value =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::RESULT_NAME_VALUE))]
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

        model_type =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::MODEL_TYPE))]
            ;

        opt_pack_type_value =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::OPTION_PKG_TYPE_VALUE))]
            ;

        transient_ref_name =
            (composite_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::TRANS_REF_NAME))]
            ;

        model_or_value =
            (identifier | math_expression) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::MODEL_NAME)(adm_boost_common::VALUE))]
            ;

        model_or_value_or_node =
            (identifier | math_expression) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::MODEL_NAME)(adm_boost_common::VALUE)(adm_boost_common::GENERALNODE))]
            ;

        model_or_node =
            identifier  [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::MODEL_NAME)(adm_boost_common::GENERALNODE))]
            ;

        value_or_node =
            identifier  [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::VALUE)(adm_boost_common::GENERALNODE))]
            ;

        general_node =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::GENERALNODE))]
            ;

        AREA_VALUE =
            (identifier | math_expression) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::AREA_VALUE))]
            ;

        CONTROL_DEV_VALUE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::CONTROL_DEV_VALUE))]
            ;

        COUPLING_VALUE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::COUPLING_VALUE))]
            ;

        FREQ_VALUE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::FREQ_VALUE))]
            ;

        FUNC_ARG_VALUE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::FUNC_ARG_VALUE))]
            ;

        FUNC_NAME_VALUE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::FUNC_NAME_VALUE))]
            ;

        FUND_FREQ_VALUE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::FUND_FREQ_VALUE))]
            ;

        GAIN_VALUE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::GAIN_VALUE))]
            ;

        GENERAL_VALUE =
            (composite_math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::GENERAL_VALUE))]
            ;

        TRANSCONDUCTANCE_VALUE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::TRANSCONDUCTANCE_VALUE))]
            ;

        POSNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::POSNODE))]
            ;

        NEGNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::NEGNODE))]
            ;

        DRAINNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DRAINNODE))]
            ;

        GATENODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::GATENODE))]
            ;

        SOURCENODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::SOURCENODE))]
            ;

        ANODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::ANODE))]
            ;

        POSCONTROLNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::POSCONTROLNODE))]
            ;

        NEGCONTROLNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::NEGCONTROLNODE))]
            ;

        COLLECTORNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::COLLECTORNODE))]
            ;

        BASENODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::BASENODE))]
            ;

        EMITTERNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::EMITTERNODE))]
            ;

        COLLECTORPRIMENODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::COLLECTORPRIMENODE))]
            ;

        BASEPRIMENODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::BASEPRIMENODE))]
            ;

        EMITTERPRIMENODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::EMITTERPRIMENODE))]
            ;

        POSSWITCHNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::POSSWITCHNODE))]
            ;

        NEGSWITCHNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::NEGSWITCHNODE))]
            ;

        APORTPOSNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::APORTPOSNODE))]
            ;

        APORTNEGNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::APORTNEGNODE))]
            ;

        BPORTPOSNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::BPORTPOSNODE))]
            ;

        BPORTNEGNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::BPORTNEGNODE))]
            ;

        SUBSTRATENODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::SUBSTRATENODE))]
            ;

        TEMPERATURENODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::TEMPERATURENODE))]
            ;

        LOWOUTPUTNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::LOWOUTPUTNODE))]
            ;

        HIGHOUTPUTNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::HIGHOUTPUTNODE))]
            ;

        INPUTREFERENCENODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::INPUTREFERENCENODE))]
            ;

        INPUTNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::INPUTNODE))]
            ;

        OUTPUTNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::OUTPUTNODE))]
            ;

        ACCELERATIONNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::ACCELERATIONNODE))]
            ;

        VELOCITYNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::VELOCITYNODE))]
            ;

        POSITIONNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::POSITIONNODE))]
            ;

        THERMALNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::THERMALNODE))]
            ;

        EXTERNALBODYCONTACTNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::EXTERNALBODYCONTACTNODE))]
            ;

        INTERNALBODYCONTACTNODE =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::INTERNALBODYCONTACTNODE))]
            ;

        expression =
            composite_math_expression [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::EXPRESSION))]
            ;

        no_curly_brace_expression_sym =
            no_curly_brace_expression [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::EXPRESSION))]
            ;

        lin_sweep_type =
            qi::as_string[no_case[lit("LIN")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::SWEEP_TYPE))]
            ;

        oct_sweep_type =
            qi::as_string[no_case[lit("OCT")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::SWEEP_TYPE))]
            ;

        dec_sweep_type =
            qi::as_string[no_case[lit("DEC")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::SWEEP_TYPE))]
            ;

        list_sweep_type =
            qi::as_string[no_case[lit("LIST")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::SWEEP_TYPE))]
            ;

        transient_func_type =
            pulse_trans_type | sin_trans_type | exp_trans_type | pwl_trans_type | sffm_trans_type
            ;

        pulse_trans_type =
            qi::as_string[no_case[lit("PULSE")]] [symbol_adder(_val, boost::spirit::_1,vector_of<data_model_type>(adm_boost_common::TRANS_FUNC_TYPE))]
            ;

        sin_trans_type =
            qi::as_string[no_case[lit("SIN")]] [symbol_adder(_val, boost::spirit::_1,vector_of<data_model_type>(adm_boost_common::TRANS_FUNC_TYPE))]
            ;

        exp_trans_type =
            qi::as_string[no_case[lit("EXP")]] [symbol_adder(_val, boost::spirit::_1,vector_of<data_model_type>(adm_boost_common::TRANS_FUNC_TYPE))]
            ;

        pwl_trans_type =
            qi::as_string[no_case[lit("PWL")]] [symbol_adder(_val, boost::spirit::_1,vector_of<data_model_type>(adm_boost_common::TRANS_FUNC_TYPE))]
            ;

        sffm_trans_type =
            qi::as_string[no_case[lit("SFFM")]] [symbol_adder(_val, boost::spirit::_1,vector_of<data_model_type>(adm_boost_common::TRANS_FUNC_TYPE))]
            ;

        pulse_trans =
            pulse_trans_type >> -white_space >> -lit("(") >> -white_space >> +(transient_ref_name >> -white_space) >> -white_space >> -lit(")")
            ;

        sin_trans =
            sin_trans_type >> -white_space >> -lit("(") >> -white_space >> +(transient_ref_name >> -white_space) >> -white_space >> -lit(")")
            ;

        exp_trans =
            exp_trans_type >> -white_space >> -lit("(") >> -white_space >> +(transient_ref_name >> -white_space) >> -white_space >> -lit(")")
            ;

        pwl_trans =
            pwl_trans_type >>
            hold[-white_space >> -lit("(") >> -white_space >> +(transient_ref_name >> -white_space % (lit(",") >> -white_space)) >> -white_space >> -lit(")")] |
            hold[+(-lit("(") >> -white_space >> transient_ref_name >> -white_space >> lit(",") >> -white_space >> transient_ref_name >> -white_space >> -lit(")"))]
            ;

        sffm_trans =
            sffm_trans_type >> -white_space >> -lit("(") >> -white_space >> +(transient_ref_name >> -white_space) >> -white_space >> -lit(")")
            ;

        transient =
            pulse_trans | sin_trans | exp_trans | pwl_trans | sffm_trans
            ;

        transient_or_ac_dc =
            hold[transient] |
            hold[dc_value_type >> lit("=") >> dc_value_value] |
            hold[dc_value_type >> white_space >> dc_value_value] |
            hold[ac_value_type >> white_space >> ac_mag_value >> -(white_space >> !transient_func_type >> !dc_value_type >> ac_phase_value)] |
            hold[!ac_value_type >> !transient_func_type >> dc_value_value]
            ;

        output_variable =
            (output_variable_expression | math_expression | identifier) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::OUTPUT_VARIABLE))]
            ;

        simple_v_output =
            simple_v_output_expression >> qi::as_string[lit("=")] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::OUTPUT_VARIABLE))]
            ;

        abm_expression =
            voltage_type >> -white_space >> lit("=") >> -white_space >> lit("{") >> -white_space >> table >> -white_space >> lit("}") |
            current_type >> -white_space >> lit("=") >> -white_space >> lit("{") >> -white_space >> table >> -white_space >> lit("}") |
            voltage_type >> -white_space >> lit("=") >> -white_space >> expression |
            current_type >> -white_space >> lit("=") >> -white_space >> expression
            ;

        control_expression =
            hold[control_str >> -white_space >> lit("=") >> -white_space >> expression] |
            hold[control_str >> -white_space >> expression]
            ;

        analysis_type =
            (qi::as_string[no_case[lit("DC")]] |
             qi::as_string[no_case[lit("AC")]] |
             qi::as_string[no_case[lit("TRAN")]] |
             qi::as_string[no_case[lit("TR")]] |
             qi::as_string[no_case[lit("SENS")]] |
             qi::as_string[no_case[lit("HOMOTOPY")]] |
             qi::as_string[no_case[lit("MPDE")]] |
             qi::as_string[no_case[lit("HB")]])  [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::ANALYSIS_TYPE))]
            ;

        preprocess_keyword =
            (qi::as_string[no_case[lit("ADDRESISTORS")]] |
             qi::as_string[no_case[lit("REMOVEUNUSED")]] |
             qi::as_string[no_case[lit("REPLACEGROUND")]]) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::PREPROCESS_KEYWORD))]
            ;

        param_type =
            qi::as_string[no_case[lit("param")]]  [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::VALUE))]
            ;

        params_set_type =
            qi::as_string[no_case[lit("PARAMS:")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::PARAMS_HEADER))]
            ;

        on_type =
            qi::as_string[no_case[lit("ON")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::ON))]
            ;

        off_type =
            qi::as_string[no_case[lit("OFF")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::OFF))]
            ;

        table_type =
            qi::as_string[no_case[lit("TABLE")]]  [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::TABLE))]
            ;

        table =
            table_type >> -white_space >> expression >> -hold[-white_space >> lit("=")] >>
            +(-white_space >> lit("(") >> -hold[-white_space >> lit("(")] >> -white_space >> table_param_value >>
                    -white_space >> -lit(",") >> -white_space >> table_param_value >> -white_space >> lit(")")) >> -hold[-white_space >> lit(")")]

            ;

        poly_type =
            qi::as_string[no_case[lit("POLY")]]  [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::POLY))]
            ;

        poly =
            poly_type >> lit("(") >> param_value >> lit(")")
            ;

        value_type =
            qi::as_string[no_case[lit("VALUE")]]  [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::VALUE_KEYWORD))]
            ;

        value_expression =
            hold[value_type >> -white_space >> lit("=") >> -white_space >> expression] |
            hold[value_type >> -white_space >> expression] |
            hold[value_type >> -white_space >> lit("=") >> -white_space >> no_curly_brace_expression_sym] |
            hold[value_type >> -white_space >> no_curly_brace_expression_sym]
            ;

        objfunc_type =
            qi::as_string[no_case[lit("objfunc")]]  [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::VALUE))]
            ;

        circuit_params =
            param_name >> *(-white_space >> lit(",") >> param_name)
            ;

        lib_entry =
            identifier [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::LIB_ENTRY))]
            ;

        // STARTING POINT ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        netlist_line = comment | ((analog_device | directive) >> -(-white_space >> inline_comment))
            ;

        // DIRECTIVES ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        directive =
            ac_dir | dcvolt_dir | dc_dir | ends_dir | endl_dir | end_dir | func_dir | global_param_dir | global_dir | hb_dir | inc_dir | ic_dir | lib_dir | lin_dir | measure_dir | model_dir |
            four_dir | nodeset_dir | options_dir | op_dir | preprocess_dir | print_dir | param_dir | save_dir | sens_dir | step_dir | subckt_dir | tran_dir | mor_dir | mpde_dir;
        ;

        ac_dir_type =
            qi::as_string[no_case[lit(".AC")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        ac_dir =
            ac_dir_type >> white_space >> (lin_sweep_type | dec_sweep_type | oct_sweep_type) >> white_space >> points_value >> white_space >> start_freq_value >> white_space >> end_freq_value
            ;

        dc_dir_type =
            qi::as_string[no_case[lit(".DC")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        dc_dir =
            dc_dir_type >> *(white_space >> sweep_param_value)
            ;

        dcvolt_dir_type =
            qi::as_string[no_case[lit(".DCVOLT")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        dcvolt_dir =
            dcvolt_dir_type >>
            hold[+(white_space >> -voltage_type >> -white_space >> -lit("(") >> -white_space >> general_node >> -white_space >> -lit(")") >> -white_space >> -lit("=") >> -white_space >> GENERAL_VALUE)]
            ;

        end_dir_type =
            qi::as_string[no_case[lit(".END")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        end_dir =
            end_dir_type.alias();
        ;

        ends_dir_type =
            qi::as_string[no_case[lit(".ENDS")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        ends_dir =
            ends_dir_type >> -(white_space >> param_value)
            ;

        endl_dir_type =
            qi::as_string[no_case[lit(".ENDL")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        endl_dir =
            endl_dir_type >> -(white_space >> lib_entry)
            ;

        four_dir_type =
            qi::as_string[no_case[lit(".FOUR")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        four_dir =
            four_dir_type >> white_space >> FREQ_VALUE >> *(white_space >> output_variable)
            ;

        func_dir_type =
            qi::as_string[no_case[lit(".FUNC")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        func_dir =
            func_dir_type >> white_space >> FUNC_NAME_VALUE >> -white_space >> lit("(") >> -(FUNC_ARG_VALUE % lit(",")) >> lit(")") >> white_space >> FUNC_EXPRESSION
            ;

        global_dir_type =
            qi::as_string[no_case[lit(".GLOBAL")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        global_dir =
            global_dir_type >> *(white_space >> general_node)
            ;

        global_param_dir_type =
            qi::as_string[no_case[lit(".GLOBAL_PARAM")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        global_param_dir =
            global_param_dir_type >> +(white_space >> param_value_pair)
            ;

        hb_dir_type =
            qi::as_string[no_case[lit(".HB")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        hb_dir =
            hb_dir_type >> white_space >> FUND_FREQ_VALUE
            ;

        ic_dir_type =
            qi::as_string[no_case[lit(".IC")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        ic_dir_type_alt =
            qi::as_string[no_case[lit(".INITCOND")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        ic_dir =
            ic_dir_type_alt | ic_dir_type >>
            hold[+(white_space >> -voltage_type >> -white_space >> -lit("(") >> -white_space >> general_node >> -white_space >> -lit(")") >> -white_space >> -lit("=") >> -white_space >> GENERAL_VALUE)]
            ;

        inc_dir_type =
            (qi::as_string[no_case[lit(".INCLUDE")]] | qi::as_string[no_case[lit(".INC")]]) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        inc_dir =
            inc_dir_type >> white_space >> filename
            ;

        lib_dir_type =
            qi::as_string[no_case[lit(".LIB")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        lib_dir =
            hold[lib_dir_type >> white_space >> filename >> white_space >> lib_entry] |
            hold[lib_dir_type >> white_space >> lib_entry] 
            ;

        lin_dir_type =
            qi::as_string[no_case[lit(".LIN")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        lin_dir =
            lin_dir_type >> *(white_space >> param_value_pair)
            ;

        measure_dir_type =
            qi::as_string[no_case[lit(".MEASURE")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        measure_dir =
            hold[measure_dir_type >> white_space >> analysis_type >> white_space >> result_name_value >> white_space >> measurement_type >> -white_space >> lit("=") >> -white_space >> variable_expr_or_value] | 
            hold[measure_dir_type >> white_space >> analysis_type >> white_space >> result_name_value >> white_space >> measurement_type >> white_space >>
            variable_expr_or_value >> -(lit("=") >> variable_expr_or_value) >> *(white_space >> measure_param_value_pair) >> -(white_space >> measurement_qualifier >> white_space >> 
            variable_expr_or_value >> -(lit("=") >> variable_expr_or_value) >> *(white_space >> measure_param_value_pair))] 
            ;

        model_dir_type =
            qi::as_string[no_case[lit(".MODEL")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        model_dir =
            model_dir_type >> white_space >> model_name >> white_space >> model_type >> -white_space >> -lit("(") >> -white_space >> -param_value_pair >> *(-(-white_space >> lit(",")) >> white_space >> param_value_pair) >> -white_space >> -lit(")")
            ;

        nodeset_dir_type =
            qi::as_string[no_case[lit(".NODESET")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        nodeset_dir =
            nodeset_dir_type >>
            hold[+(white_space >> -voltage_type >> -white_space >> -lit("(") >> -white_space >> general_node >> -white_space >> -lit(")") >> -white_space >> -lit("=") >> -white_space >> GENERAL_VALUE)]
            ;

        options_dir_type =
            qi::as_string[no_case[lit(".OPTIONS")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        options_dir =
            options_dir_type >> white_space >> opt_pack_type_value >> *(white_space >> param_value_pair)
            ;

        op_dir_type =
            qi::as_string[no_case[lit(".OP")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        op_dir =
            op_dir_type.alias();
        ;

        param_dir_type =
            qi::as_string[no_case[lit(".PARAM")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        param_dir =
            param_dir_type >> +(white_space >> param_value_pair >> -lit(","))
            ;

        preprocess_dir_type =
            qi::as_string[no_case[lit(".PREPROCESS")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        preprocess_dir =
            preprocess_dir_type >> white_space >> preprocess_keyword >> +(white_space >> list_param_value)
            ;

        print_dir_type =
            qi::as_string[no_case[lit(".PRINT")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        print_dir =
            print_dir_type >> white_space >> analysis_type >> hold[*(white_space >> param_value_pair)] >> *(white_space >> output_variable)
            ;

        save_dir_type =
            qi::as_string[no_case[lit(".SAVE")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        save_dir =
            save_dir_type >> *(white_space >> param_value_pair)
            ;

        sens_dir_type =
            qi::as_string[no_case[lit(".SENS")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        sens_dir =
            sens_dir_type >> *(white_space >> param_value_pair)
            ;

        step_dir_type =
            qi::as_string[no_case[lit(".STEP")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        step_dir =
            step_dir_type >> *(white_space >> sweep_param_value)
            ;

        subckt_dir_type =
            qi::as_string[no_case[lit(".SUBCKT")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        subckt_dir =

            hold[subckt_dir_type >> white_space >> devname >> hold[+(white_space >> !param_value_pair >> subckt_directive_param_value)] >> *(white_space >> param_value_pair)] |
            hold[subckt_dir_type >> white_space >> devname >> +(white_space >> !params_set_type >> subckt_directive_param_value) >> -(white_space >> params_set_type >> +(white_space >> param_value_pair))]
            ;

        tran_dir_type =
            (qi::as_string[no_case[lit(".TRAN")]] |
             qi::as_string[no_case[lit(".TR")]]) [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        tran_dir =
            tran_dir_type >> white_space >>
            printStepValue >> white_space >> finalTimeValue >>
            -(white_space >> !NOOP_VALUE >> !UIC_VALUE >> !SCHEDULE_TYPE >> startTimeValue >>
                    -(white_space >> !NOOP_VALUE >> !UIC_VALUE >> !SCHEDULE_TYPE >> stepCeilingValue)) >>
            -(white_space >> NOOP_VALUE) >> -(white_space >> UIC_VALUE) >>
            -(white_space >> SCHEDULE_TYPE >> -white_space >> lit("(") >> *(-white_space >> schedule_param_value >> -white_space % lit(",")) >> lit(")"))
            ;

        mor_dir_type =
            qi::as_string[no_case[lit(".MOR")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        mor_dir =
            mor_dir_type >> restOfLine
            ;


        mpde_dir_type =
            qi::as_string[no_case[lit(".MPDE")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DIRECTIVE_TYPE))]
            ;

        mpde_dir =
            mpde_dir_type >> restOfLine
            ;

        // ANALOG DEVICES  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


        analog_device =
            (bjt | capacitor | digital_dev | diode | generic_switch | current_ctrl_current_src | current_ctrl_switch | current_ctrl_voltage_src | indep_current_src | indep_voltage_src | inductor | jfet | lossless_trans_line | lossy_trans_line | mesfet | mosfet | mututal_inductor | non_linear_dep_src | port | resistor | subcircuit | voltage_ctrl_current_src | voltage_ctrl_switch | voltage_ctrl_voltage_src)
            ;

        bjt_dev_type =
            qi::as_string[no_case[char_("Q")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        bjt =
            (
             hold[bjt_dev_type >> -devname >> white_space >> COLLECTORNODE >> white_space >> BASENODE >> white_space >> EMITTERNODE >> white_space >> SUBSTRATENODE >> white_space >> COLLECTORPRIMENODE >> white_space >> BASEPRIMENODE >> white_space >> EMITTERPRIMENODE >> white_space >> model_name] |
             hold[bjt_dev_type >> -devname >> white_space >> COLLECTORNODE >> white_space >> BASENODE >> white_space >> EMITTERNODE >> white_space >> SUBSTRATENODE >> white_space >> model_name >> white_space >> !param_value_pair >> AREA_VALUE] |
             hold[bjt_dev_type >> -devname >> white_space >> COLLECTORNODE >> white_space >> BASENODE >> white_space >> EMITTERNODE >> white_space >> THERMALNODE >> white_space >> vbic_model_type >> vbic_model_name] |
             hold[bjt_dev_type >> -devname >> white_space >> COLLECTORNODE >> white_space >> BASENODE >> white_space >> EMITTERNODE >> white_space >> lit("[") >> SUBSTRATENODE >> lit("]") >> white_space >> model_name >> -(white_space >> !param_value_pair >> AREA_VALUE)] |
             hold[bjt_dev_type >> -devname >> white_space >> COLLECTORNODE >> white_space >> BASENODE >> white_space >> EMITTERNODE >> white_space >> model_name >> -(white_space >> !param_value_pair >> AREA_VALUE)]
            ) >> *(white_space >> param_value_pair)
            ;

        capacitor_dev_type =
            qi::as_string[no_case[char_("C")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        capacitor =
            capacitor_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> -( white_space >> !param_value_pair >> model_or_value)
            >> -(white_space >> !param_value_pair >> model_or_value) >> *(white_space >> param_value_pair)
            ;

        //debug(capacitor);

        current_ctrl_current_src_dev_type =
            qi::as_string[no_case[char_("F")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        current_ctrl_current_src =
            hold[current_ctrl_current_src_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> poly >> +(white_space >> poly_param_value)] |
            hold[current_ctrl_current_src_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> control_param_value >> white_space >> GAIN_VALUE]
            ;

        current_ctrl_switch_dev_type =
            qi::as_string[no_case[char_("W")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        current_ctrl_switch =
            current_ctrl_switch_dev_type >> -devname >> white_space >> POSSWITCHNODE >> white_space >> NEGSWITCHNODE >> white_space >> control_param_value >> white_space >> model_name >> -(white_space >> (on_type | off_type))
            ;

        current_ctrl_voltage_src_dev_type =
            qi::as_string[no_case[char_("H")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        current_ctrl_voltage_src =
            hold[current_ctrl_voltage_src_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> poly >> +(white_space >> poly_param_value)] |
            hold[current_ctrl_voltage_src_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> value_expression] |
            hold[current_ctrl_voltage_src_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> table] |
            hold[current_ctrl_voltage_src_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> control_param_value >> white_space >> GAIN_VALUE]
            ;

        digital_dev_type =
            qi::as_string[no_case[char_("Y")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        digital_dev =
            digital_dev_type >> devtype >> white_space >> devname >> +(white_space >> !param_value_pair >> model_or_node) >> *(white_space >> param_value_pair)
            ;

        diode_dev_type =
            qi::as_string[no_case[char_("D")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        diode =
            diode_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> !param_value_pair >> model_name
            >> -(white_space >> !param_value_pair >> model_or_value) >> *(white_space >> param_value_pair)
            ;

        indep_current_src_type =
            qi::as_string[no_case[char_("I")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        indep_current_src =
            indep_current_src_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> *(white_space >> transient_or_ac_dc)
            ;

        indep_voltage_src_type =
            qi::as_string[no_case[char_("V")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        indep_voltage_src =
            indep_voltage_src_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> *(white_space >> transient_or_ac_dc)
            ;

        inductor_dev_type =
            qi::as_string[no_case[char_("L")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        inductor =
            inductor_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> model_or_value >> -(white_space >> !param_value_pair >> model_or_value) >> *(white_space >> param_value_pair)
            ;

        jfet_dev_type =
            qi::as_string[no_case[char_("J")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        jfet =
            jfet_dev_type >> -devname >> white_space >> DRAINNODE >> white_space >> GATENODE >> white_space >> SOURCENODE >> white_space >> model_name >> -(white_space >> !param_value_pair >> param_value)
            >> *(white_space >> param_value_pair)
            ;

        mesfet_type =
            qi::as_string[no_case[char_("Z")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        mesfet =
            mesfet_type >> -devname >> white_space >> DRAINNODE >> white_space >> GATENODE >> white_space >> SOURCENODE >> white_space >> model_name >> *(white_space >> param_value_pair)
            ;

        mosfet_type =
            qi::as_string[no_case[char_("M")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        mosfet =
            hold[mosfet_type >> -devname >> white_space >> DRAINNODE >> white_space >> GATENODE >> white_space >> SOURCENODE >> white_space >>
            SUBSTRATENODE >> white_space >> EXTERNALBODYCONTACTNODE >> white_space >> INTERNALBODYCONTACTNODE >> white_space
            >> TEMPERATURENODE >> white_space >> !param_value_pair >> model_name 
            >> *(white_space >> *(standalone_param >> white_space) >> param_value_pair) >> *(white_space >> standalone_param)] |
            hold[mosfet_type >> -devname >> white_space >> DRAINNODE >> white_space >> GATENODE >> white_space >> SOURCENODE >> white_space >>
            SUBSTRATENODE >> white_space >> EXTERNALBODYCONTACTNODE >> white_space >> INTERNALBODYCONTACTNODE >> white_space
            >> !param_value_pair >> model_name >> *(white_space >> *(standalone_param >> white_space) >> param_value_pair) 
            >> *(white_space >> standalone_param)] |
            hold[mosfet_type >> -devname >> white_space >> DRAINNODE >> white_space >> GATENODE >> white_space >> SOURCENODE >> white_space >>
            SUBSTRATENODE >> white_space >> EXTERNALBODYCONTACTNODE >> white_space >> !param_value_pair >> model_name 
            >> *(white_space >> *(standalone_param >> white_space) >> param_value_pair) >> *(white_space >> standalone_param)] |
            hold[mosfet_type >> -devname >> white_space >> DRAINNODE >> white_space >> GATENODE >> white_space >> SOURCENODE >> white_space >>
            SUBSTRATENODE >> white_space >> !param_value_pair >> model_name >> *(white_space >> param_value_pair)]
            ;

        mutual_inductor_dev_type =
            qi::as_string[no_case[char_("K")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        control_inductor_dev_type =
            qi::as_string[no_case[char_("L")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::CONTROL_DEVICE))]
            ;

        mututal_inductor =
            mutual_inductor_dev_type >> -devname >> +(white_space >> control_inductor_dev_type >> -control_inductor_dev_name) >> white_space >> COUPLING_VALUE >> -(white_space >> model_name)
            ;

        non_linear_dep_src_type =
            qi::as_string[no_case[char_("B")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        non_linear_dep_src =
            non_linear_dep_src_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> abm_expression
            ;

        port_dev_type =
            qi::as_string[no_case[char_("P")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        port =
            port_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> -( white_space >> !param_value_pair >> model_or_value)
            >> -(white_space >> !param_value_pair >> model_or_value) >> 
            *(white_space >> (port_param_value_pair | port_param_double_value_pair | port_param_triple_value_pair | port_param_quad_value_pair | port_param_quint_value_pair | port_param_sextuplet_value_pair | port_param_sextuplet_value_pair_last | port_param_quint_value_pair_last | port_param_quad_value_pair_last | port_param_triple_value_pair_last | port_param_double_value_pair_last | port_param_value_pair_last))
            ;

        resistor_dev_type =
            qi::as_string[no_case[char_("R")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        resistor =
            resistor_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> -( white_space >> !param_value_pair >> model_or_value)
            >> -(white_space >> !param_value_pair >> model_or_value) >> *(white_space >> param_value_pair)
            ;

        subcircuit_type =
            qi::as_string[no_case[char_("X")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        subcircuit =
            hold[subcircuit_type >> -devname >>  +(white_space >> !params_set_type >> subckt_device_param_value) >> -(white_space >> params_set_type >> +(white_space >> param_value_pair))] |
            hold[subcircuit_type >> -devname >>  +(white_space >> !param_value_pair >> subckt_device_param_value) >> *(white_space >> param_value_pair)]
            ;

        lossless_trans_line_type =
            qi::as_string[no_case[char_("T")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        lossless_trans_line =
            lossless_trans_line_type >> devname >> white_space >> APORTPOSNODE >> white_space >> APORTNEGNODE >> white_space >> BPORTPOSNODE >> white_space >> BPORTNEGNODE >> *(white_space >> param_value_pair)
            ;

        lossy_trans_line_type =
            qi::as_string[no_case[char_("O")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        lossy_trans_line =
            lossy_trans_line_type >> devname >> white_space >> APORTPOSNODE >> white_space >> APORTNEGNODE >> white_space >> BPORTPOSNODE >> white_space >> BPORTNEGNODE >> -(white_space >> model_name)
            ;

        voltage_ctrl_current_src_dev_type =
            qi::as_string[no_case[char_("G")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        voltage_ctrl_current_src =
            hold[voltage_ctrl_current_src_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> poly >> +(white_space >> poly_param_value)] |
            hold[voltage_ctrl_current_src_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> value_expression] |
            hold[voltage_ctrl_current_src_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> table] |
            hold[voltage_ctrl_current_src_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> POSCONTROLNODE >> white_space >> NEGCONTROLNODE >> white_space >> TRANSCONDUCTANCE_VALUE]
            ;

        voltage_ctrl_switch_dev_type =
            qi::as_string[no_case[char_("S")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        voltage_ctrl_switch =
            voltage_ctrl_switch_dev_type >> -devname >> white_space >> POSSWITCHNODE >> white_space >> NEGSWITCHNODE >> white_space >> POSCONTROLNODE >> white_space >> NEGCONTROLNODE >>
            white_space >> model_name >> -(white_space >> (on_type | off_type))
            ;

        generic_switch_dev_type =
            qi::as_string[no_case[lit("SW")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        generic_switch =
            generic_switch_dev_type >> -devname >> white_space >> POSSWITCHNODE >> white_space >> NEGSWITCHNODE >> white_space >> model_name >> -(white_space >> (on_type | off_type)) >>
            white_space >> control_expression
            ;

        voltage_ctrl_voltage_src_dev_type =
            qi::as_string[no_case[char_("E")]] [symbol_adder(_val, boost::spirit::_1, vector_of<data_model_type>(adm_boost_common::DEVICE_ID))]
            ;

        voltage_ctrl_voltage_src =
            hold[voltage_ctrl_voltage_src_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> poly >> +(white_space >> poly_param_value)] |
            hold[voltage_ctrl_voltage_src_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> value_expression] |
            hold[voltage_ctrl_voltage_src_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> table] |
            hold[voltage_ctrl_voltage_src_dev_type >> -devname >> white_space >> POSNODE >> white_space >> NEGNODE >> white_space >> POSCONTROLNODE >> white_space >> NEGCONTROLNODE >> white_space >> GAIN_VALUE]
            ;
    }
};

#endif

