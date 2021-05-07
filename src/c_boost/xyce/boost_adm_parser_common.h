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


#if !defined(ADM_BOOST_COMMON)
#define ADM_BOOST_COMMON
#define FUSION_MAX_VECTOR_SIZE 15
#include <boost/config/warning_disable.hpp>
#include <boost/spirit/include/qi.hpp>
#include <boost/spirit/include/phoenix_core.hpp>
#include <boost/spirit/include/phoenix_operator.hpp>
#include <boost/spirit/include/phoenix_fusion.hpp>
#include <boost/spirit/include/phoenix_stl.hpp>
#include <boost/spirit/include/phoenix_object.hpp>

#include <vector>
#include <iostream>

namespace adm_boost_common {
enum data_model_type
{
    DEVICE_ID, DEVICE_NAME, DIRECTIVE_TYPE, POSNODE, NEGNODE, GENERALNODE, VALUE, OPTION_PKG_TYPE_VALUE, MODEL_NAME, TRANS_FUNC_TYPE, TRANS_REF_NAME,
    PARAM_NAME, PARAM_VALUE, OUTPUT_VARIABLE, ANALYSIS_TYPE, FUNCTION_NAME, EXPRESSION, SWEEP_TYPE, INLINE_COMMENT, PARAMS_HEADER, ON, OFF,
    LIST, LIN, OCT, DEC, TABLE, VOLTAGE, CURRENT, MODEL_TYPE, COMMENT, DRAINNODE, GATENODE, SOURCENODE, ANODE, POSCONTROLNODE,
    NEGCONTROLNODE, COLLECTORNODE, BASENODE, EMITTERNODE, COLLECTORPRIMENODE, BASEPRIMENODE, EMITTERPRIMENODE, POSSWITCHNODE,
    NEGSWITCHNODE, APORTPOSNODE, APORTNEGNODE, BPORTPOSNODE, BPORTNEGNODE, SUBSTRATENODE, TEMPERATURENODE, LOWOUTPUTNODE, HIGHOUTPUTNODE,
    INPUTREFERENCENODE, INPUTNODE, OUTPUTNODE, ACCELERATIONNODE, VELOCITYNODE, POSITIONNODE, FILENAME, CONTROL_DEVICE, CONTROL_DEV_VALUE, TITLE,
    VALUE_KEYWORD, GAIN_VALUE, TRANSCONDUCTANCE_VALUE, VBIC_MODEL, VBIC_MODEL_NAME, THERMALNODE, AREA_VALUE, LIST_PARAM_VALUE, POLY, POLY_VALUE,
    CONTROL_DEVICE_NAME, PRINT_STEP_VALUE, FINAL_TIME_VALUE, START_TIME_VALUE, STEP_CEILING_VALUE, COUPLING_VALUE, LIB_ENTRY, DC_VALUE,
    DC_VALUE_VALUE, AC_VALUE, AC_MAG_VALUE, AC_PHASE_VALUE, RESULT_NAME_VALUE, MEASUREMENT_TYPE, EXTERNALBODYCONTACTNODE, INTERNALBODYCONTACTNODE,
    PREPROCESS_KEYWORD, CONTROL, TABLE_PARAM_VALUE, POLY_PARAM_VALUE, CONTROL_PARAM_VALUE, SUBCKT_DIRECTIVE_PARAM_VALUE,
    SUBCKT_DEVICE_PARAM_VALUE, POINTS_VALUE, START_FREQ_VALUE, END_FREQ_VALUE, GENERAL_VALUE, FUND_FREQ_VALUE, FREQ_VALUE, FUNC_ARG_VALUE,
    FUNC_NAME_VALUE, FUNC_EXPRESSION, NOOP_VALUE, UIC_VALUE, SCHEDULE_TYPE, SCHEDULE_PARAM_VALUE, SWEEP_PARAM_VALUE, TEMP_VALUE, REST_OF_LINE,
    DIG_DEV_TYPE, UNKNOWN_NODE, DEFAULT_PARAM_NAME, MEASURE_TYPE, MEASURE_QUALIFIER, MEASURE_PARAM_NAME, MEASURE_PARAM_VALUE, VARIABLE_EXPR_OR_VALUE,
    STANDALONE_PARAM, DATA_TABLE_NAME, DATA_PARAM_NAME, DATA_PARAM_VALUE, BLOCK_DELIMITER, CONDITIONAL_STATEMENT, 
    BINNED_MODEL_NAME, DC_SWEEP_DEV, DC_SWEEP_PARAM, DC_SWEEP_START, DC_SWEEP_STOP, DC_SWEEP_STEP
};

static const char* data_model_type_strs[] = {"DEVICE_ID", "DEVICE_NAME", "DIRECTIVE_TYPE", "POSNODE", "NEGNODE", "GENERALNODE", "VALUE",
    "OPTION_PKG_TYPE_VALUE", "MODEL_NAME", "TRANS_FUNC_TYPE", "TRANS_REF_NAME", "PARAM_NAME", "PARAM_VALUE", "OUTPUT_VARIABLE", "ANALYSIS_TYPE",
    "FUNCTION_NAME", "EXPRESSION", "SWEEP_TYPE", "INLINE_COMMENT", "PARAMS_HEADER", "ON", "OFF", "LIST", "LIN", "OCT", "DEC", "TABLE",
    "VOLTAGE", "CURRENT", "MODEL_TYPE", "COMMENT", "DRAINNODE", "GATENODE", "SOURCENODE", "ANODE", "POSCONTROLNODE",
    "NEGCONTROLNODE", "COLLECTORNODE", "BASENODE", "EMITTERNODE", "COLLECTORPRIMENODE", "BASEPRIMENODE", "EMITTERPRIMENODE",
    "POSSWITCHNODE", "NEGSWITCHNODE", "APORTPOSNODE", "APORTNEGNODE", "BPORTPOSNODE", "BPORTNEGNODE", "SUBSTRATENODE",
    "TEMPERATURENODE", "LOWOUTPUTNODE", "HIGHOUTPUTNODE", "INPUTREFERENCENODE", "INPUTNODE", "OUTPUTNODE", "ACCELERATIONNODE",
    "VELOCITYNODE", "POSITIONNODE", "FILENAME", "CONTROL_DEVICE", "CONTROL_DEV_VALUE", "TITLE", "VALUE_KEYWORD", "GAIN_VALUE",
    "TRANSCONDUCTANCE_VALUE", "VBIC_MODEL", "VBIC_MODEL_NAME", "THERMALNODE", "AREA_VALUE", "LIST_PARAM_VALUE", "POLY", "POLY_VALUE",
    "CONTROL_DEVICE_NAME", "PRINT_STEP_VALUE", "FINAL_TIME_VALUE", "START_TIME_VALUE", "STEP_CEILING_VALUE", "COUPLING_VALUE", "LIB_ENTRY",
    "DC_VALUE", "DC_VALUE_VALUE", "AC_VALUE", "AC_MAG_VALUE", "AC_PHASE_VALUE", "RESULT_NAME_VALUE", "MEASUREMENT_TYPE",
    "EXTERNALBODYCONTACTNODE", "INTERNALBODYCONTACTNODE", "PREPROCESS_KEYWORD", "CONTROL", "TABLE_PARAM_VALUE", "POLY_PARAM_VALUE",
    "CONTROL_PARAM_VALUE", "SUBCKT_DIRECTIVE_PARAM_VALUE", "SUBCKT_DEVICE_PARAM_VALUE", "POINTS_VALUE", "START_FREQ_VALUE",
    "END_FREQ_VALUE", "GENERAL_VALUE", "FUND_FREQ_VALUE", "FREQ_VALUE", "FUNC_ARG_VALUE", "FUNC_NAME_VALUE", "FUNC_EXPRESSION",
    "NOOP_VALUE", "UIC_VALUE", "SCHEDULE_TYPE", "SCHEDULE_PARAM_VALUE", "SWEEP_PARAM_VALUE", "TEMP_VALUE", "REST_OF_LINE", "DIG_DEV_TYPE",
    "UNKNOWN_NODE", "DEFAULT_PARAM_NAME", "MEASURE_TYPE", "MEASURE_QUALIFIER", "MEASURE_PARAM_NAME", "MEASURE_PARAM_VALUE", "VARIABLE_EXPR_OR_VALUE",
    "STANDALONE_PARAM", "DATA_TABLE_NAME", "DATA_PARAM_NAME", "DATA_PARAM_VALUE", "BLOCK_DELIMITER", "CONDITIONAL_STATEMENT",
    "BINNED_MODEL_NAME", "DC_SWEEP_DEV", "DC_SWEEP_PARAM", "DC_SWEEP_START", "DC_SWEEP_STOP", "DC_SWEEP_STEP"
};

struct netlist_statement_object {
    std::vector<data_model_type> candidate_types;
    std::string value;
};

inline std::ostream& operator<< (std::ostream& os, const netlist_statement_object nso) {
    std::cout << "{" << nso.value << ", [";

    for(int i = 0; i < nso.candidate_types.size()-1; i++)
        std::cout << data_model_type_strs[nso.candidate_types[i]] << ", ";

    std::cout <<data_model_type_strs[nso.candidate_types[nso.candidate_types.size()-1]];

    std::cout << "]} ";
    return os;
}

inline std::string getDataModelTypeStr(const netlist_statement_object nso) {
    std::string dataStr;
    dataStr = data_model_type_strs[nso.candidate_types[nso.candidate_types.size()-1]];

    return dataStr;
}

template <typename ELEMENT_TYPE > struct vector_of
: public std::vector<ELEMENT_TYPE>
{
    vector_of(const ELEMENT_TYPE& t)
    {
        (*this)(t);
    }
    vector_of& operator()(const ELEMENT_TYPE& t)
    {
        this->push_back(t);
        return *this;
    }
};

struct symbol_adder_impl
{
    template <class, class, class>
        struct result { typedef void type;};

    template <class N, class S, class E>
        void operator () (N & nso, S & v, E const& types) const
        {
            nso.value = v;

            for(int i = 0; i < types.size(); i++)
                nso.candidate_types.push_back((data_model_type)types[i]);
        }
};

const boost::phoenix::function<symbol_adder_impl> symbol_adder =
boost::phoenix::function<symbol_adder_impl>(symbol_adder_impl());

typedef std::string::const_iterator iterator_type;

}


#endif
