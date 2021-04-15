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


#include "parser_interface.hpp"
#include "tspice_parser_interface.hpp"
#include "hspice_parser_interface.hpp"
#include "pspice_parser_interface.hpp"
#include "spectre_parser_interface.hpp"
#include "xyce_parser_interface.hpp"

#include <boost/algorithm/string.hpp>

#include <fstream>
#include <iostream>

std::string getLineNumsString (BoostParsedLine parsedLine) {
    std::string lineNumsString = "[";

    for (int i = 0; i < len(parsedLine.linenums); i++) {
        // extracts the line number from the boost python list
        std::string num = boost::python::extract<std::string>(
            boost::python::object(parsedLine.linenums[i]).attr("__str__")())();
        // add a comma if not the last element
        if (i != len(parsedLine.linenums) - 1) {
            num += ",";
        }
        lineNumsString += num;
    }
    lineNumsString += "]";
    return lineNumsString ;
}

void convert_to_parsed_objects(std::vector<adm_boost_common::netlist_statement_object> netlist_parse_results, BoostParsedLine parsedLine) {

    for(int i = 0; i < netlist_parse_results.size(); i++) {

        boost::python::list typeList;

        for(int j = 0; j < netlist_parse_results[i].candidate_types.size(); j++) {
            typeList.append(netlist_parse_results[i].candidate_types[j]);
        }

        ParseObject obj;
        obj.value = netlist_parse_results[i].value;
        obj.types = typeList;

        parsedLine.parsedObjects.append(obj);
    }
}


bool
NetlistLineReader::open(std::string filenm) {
    filename = filenm;
    inputStream = new std::ifstream(filename.c_str(), std::ifstream::in );

    tmp_line = "";
    title = "";
    current_line_num = 0;

    return inputStream->good();
}

void
NetlistLineReader::close() {
    //if(inputStream->good()) {
    inputStream->close();
    inputStream->clear();
    delete inputStream;
    //}
}


BOOST_PYTHON_MODULE(SpiritCommon)
{
    boost::python::class_<ParseObject>("ParseObject")
        .def_readwrite("value", &ParseObject::value)
        .def_readonly("types", &ParseObject::types)
        ;

    boost::python::class_<BoostParsedLine>("BoostParsedLine")
        .def_readonly("linenums", &BoostParsedLine::linenums)
        .def_readonly("filename", &BoostParsedLine::filename)
        .def_readonly("parsed_objects", &BoostParsedLine::parsedObjects)
        .def_readonly("sourceline", &BoostParsedLine::sourceLine)
        .def_readonly("error_type", &BoostParsedLine::errorType)
        .def_readonly("error_message", &BoostParsedLine::errorMessage)
        ;

    boost::python::enum_<adm_boost_common::data_model_type>("data_model_type")
        .value("DEVICE_TYPE", adm_boost_common::DEVICE_ID)
        .value("DEVICE_NAME", adm_boost_common::DEVICE_NAME)
        .value("DIRECTIVE_NAME", adm_boost_common::DIRECTIVE_TYPE)
        .value("POSNODE", adm_boost_common::POSNODE)
        .value("NEGNODE", adm_boost_common::NEGNODE)
        .value("MODEL_NAME", adm_boost_common::MODEL_NAME)
        .value("MODEL_TYPE", adm_boost_common::MODEL_TYPE)
        .value("PARAM_NAME", adm_boost_common::PARAM_NAME)
        .value("PARAM_VALUE", adm_boost_common::PARAM_VALUE)
        .value("VALUE", adm_boost_common::VALUE)
        .value("OUTPUT_VARIABLE", adm_boost_common::OUTPUT_VARIABLE)
        .value("GATENODE", adm_boost_common::GATENODE)
        .value("SOURCENODE", adm_boost_common::SOURCENODE)
        .value("DRAINNODE", adm_boost_common::DRAINNODE)
        .value("TRANS_FUNC_TYPE", adm_boost_common::TRANS_FUNC_TYPE)
        .value("TRANS_REF_NAME", adm_boost_common::TRANS_REF_NAME)
        .value("ANODE", adm_boost_common::ANODE)
        .value("POSCONTROLNODE", adm_boost_common::POSCONTROLNODE)
        .value("NEGCONTROLNODE", adm_boost_common::NEGCONTROLNODE)
        .value("EMITTERPRIMENODE", adm_boost_common::EMITTERPRIMENODE)
        .value("COLLECTORNODE", adm_boost_common::COLLECTORNODE)
        .value("BASENODE", adm_boost_common::BASENODE)
        .value("EMITTERNODE", adm_boost_common::EMITTERNODE)
        .value("COLLECTORPRIMENODE", adm_boost_common::COLLECTORPRIMENODE)
        .value("BASEPRIMENODE", adm_boost_common::BASEPRIMENODE)
        .value("POSSWITCHNODE", adm_boost_common::POSSWITCHNODE)
        .value("NEGSWITCHNODE", adm_boost_common::NEGSWITCHNODE)
        .value("APORTPOSNODE", adm_boost_common::APORTPOSNODE)
        .value("APORTNEGNODE", adm_boost_common::APORTNEGNODE)
        .value("BPORTPOSNODE", adm_boost_common::BPORTPOSNODE)
        .value("BPORTNEGNODE", adm_boost_common::BPORTNEGNODE)
        .value("SUBSTRATENODE", adm_boost_common::SUBSTRATENODE)
        .value("TEMPERATURENODE", adm_boost_common::TEMPERATURENODE)
        .value("LOWOUTPUTNODE", adm_boost_common::LOWOUTPUTNODE)
        .value("HIGHOUTPUTNODE", adm_boost_common::HIGHOUTPUTNODE)
        .value("INPUTREFERENCENODE", adm_boost_common::INPUTREFERENCENODE)
        .value("INPUTNODE", adm_boost_common::INPUTNODE)
        .value("OUTPUTNODE", adm_boost_common::OUTPUTNODE)
        .value("ACCELERATIONNODE", adm_boost_common::ACCELERATIONNODE)
        .value("VELOCITYNODE", adm_boost_common::VELOCITYNODE)
        .value("POSITIONNODE", adm_boost_common::POSITIONNODE)
        .value("GENERALNODE", adm_boost_common::GENERALNODE)
        .value("EXTERNALBODYCONTACTNODE", adm_boost_common::EXTERNALBODYCONTACTNODE)
        .value("INTERNALBODYCONTACTNODE", adm_boost_common::INTERNALBODYCONTACTNODE)
        .value("EXPRESSION", adm_boost_common::EXPRESSION)
        .value("VOLTAGE", adm_boost_common::VOLTAGE)
        .value("CURRENT", adm_boost_common::CURRENT)
        .value("PARAMS_HEADER", adm_boost_common::PARAMS_HEADER)
        .value("ON", adm_boost_common::ON)
        .value("OFF", adm_boost_common::OFF)
        .value("COMMENT", adm_boost_common::COMMENT)
        .value("FILENAME", adm_boost_common::FILENAME)
        .value("TITLE", adm_boost_common::TITLE)
        .value("OPTION_PKG_TYPE_VALUE", adm_boost_common::OPTION_PKG_TYPE_VALUE)
        .value("CONTROL_DEVICE", adm_boost_common::CONTROL_DEVICE)
        .value("CONTROL_DEV_VALUE", adm_boost_common::CONTROL_DEV_VALUE)
        .value("ANALYSIS_TYPE", adm_boost_common::ANALYSIS_TYPE)
        .value("VALUE_KEYWORD", adm_boost_common::VALUE_KEYWORD)
        .value("GAIN_VALUE", adm_boost_common::GAIN_VALUE)
        .value("TRANSCONDUCTANCE_VALUE", adm_boost_common::TRANSCONDUCTANCE_VALUE)
        .value("VBIC_MODEL", adm_boost_common::VBIC_MODEL)
        .value("VBIC_MODEL_NAME", adm_boost_common::VBIC_MODEL_NAME)
        .value("THERMALNODE", adm_boost_common::THERMALNODE)
        .value("AREA_VALUE", adm_boost_common::AREA_VALUE)
        .value("TABLE", adm_boost_common::TABLE)
        .value("LIST_PARAM_VALUE", adm_boost_common::LIST_PARAM_VALUE)
        .value("POLY", adm_boost_common::POLY)
        .value("POLY_VALUE", adm_boost_common::POLY_VALUE)
        .value("CONTROL_DEVICE_NAME", adm_boost_common::CONTROL_DEVICE_NAME)
        .value("INLINE_COMMENT", adm_boost_common::INLINE_COMMENT)
        .value("PRINT_STEP_VALUE", adm_boost_common::PRINT_STEP_VALUE)
        .value("FINAL_TIME_VALUE", adm_boost_common::FINAL_TIME_VALUE)
        .value("START_TIME_VALUE", adm_boost_common::START_TIME_VALUE)
        .value("STEP_CEILING_VALUE", adm_boost_common::STEP_CEILING_VALUE)
        .value("COUPLING_VALUE", adm_boost_common::COUPLING_VALUE)
        .value("DC_VALUE", adm_boost_common::DC_VALUE)
        .value("DC_VALUE_VALUE", adm_boost_common::DC_VALUE_VALUE)
        .value("AC_VALUE", adm_boost_common::AC_VALUE)
        .value("AC_MAG_VALUE", adm_boost_common::AC_MAG_VALUE)
        .value("AC_PHASE_VALUE", adm_boost_common::AC_PHASE_VALUE)
        .value("DC_SWEEP_DEV", adm_boost_common::DC_SWEEP_DEV)
        .value("DC_SWEEP_PARAM", adm_boost_common::DC_SWEEP_PARAM)
        .value("DC_SWEEP_START", adm_boost_common::DC_SWEEP_START)
        .value("DC_SWEEP_STOP", adm_boost_common::DC_SWEEP_STOP)
        .value("DC_SWEEP_STEP", adm_boost_common::DC_SWEEP_STEP)
        .value("RESULT_NAME_VALUE", adm_boost_common::RESULT_NAME_VALUE)
        .value("MEASUREMENT_TYPE", adm_boost_common::MEASUREMENT_TYPE)
        .value("LIB_ENTRY", adm_boost_common::LIB_ENTRY)
        .value("TABLE_PARAM_VALUE", adm_boost_common::TABLE_PARAM_VALUE)
        .value("POLY_PARAM_VALUE", adm_boost_common::POLY_PARAM_VALUE)
        .value("CONTROL_PARAM_VALUE", adm_boost_common::CONTROL_PARAM_VALUE)
        .value("SUBCKT_DIRECTIVE_PARAM_VALUE", adm_boost_common::SUBCKT_DIRECTIVE_PARAM_VALUE)
        .value("SUBCKT_DEVICE_PARAM_VALUE", adm_boost_common::SUBCKT_DEVICE_PARAM_VALUE)
        .value("SWEEP_TYPE", adm_boost_common::SWEEP_TYPE)
        .value("POINTS_VALUE", adm_boost_common::POINTS_VALUE)
        .value("START_FREQ_VALUE", adm_boost_common::START_FREQ_VALUE)
        .value("END_FREQ_VALUE", adm_boost_common::END_FREQ_VALUE)
        .value("GENERAL_VALUE", adm_boost_common::GENERAL_VALUE)
        .value("FUND_FREQ_VALUE", adm_boost_common::FUND_FREQ_VALUE)
        .value("FREQ_VALUE", adm_boost_common::FREQ_VALUE)
        .value("FUNC_ARG_VALUE", adm_boost_common::FUNC_ARG_VALUE)
        .value("FUNC_NAME_VALUE", adm_boost_common::FUNC_NAME_VALUE)
        .value("FUNC_EXPRESSION", adm_boost_common::FUNC_EXPRESSION)
        .value("PREPROCESS_KEYWORD", adm_boost_common::PREPROCESS_KEYWORD)
        .value("NOOP_VALUE", adm_boost_common::NOOP_VALUE)
        .value("UIC_VALUE", adm_boost_common::UIC_VALUE)
        .value("STANDALONE_PARAM", adm_boost_common::STANDALONE_PARAM)
        .value("SCHEDULE_TYPE", adm_boost_common::SCHEDULE_TYPE)
        .value("SCHEDULE_PARAM_VALUE", adm_boost_common::SCHEDULE_PARAM_VALUE)
        .value("SWEEP_PARAM_VALUE", adm_boost_common::SWEEP_PARAM_VALUE)
        .value("TEMP_VALUE", adm_boost_common::TEMP_VALUE)
        .value("REST_OF_LINE", adm_boost_common::REST_OF_LINE)
        .value("DIG_DEV_TYPE", adm_boost_common::DIG_DEV_TYPE)
        .value("CONTROL", adm_boost_common::CONTROL)
        .value("UNKNOWN_NODE", adm_boost_common::UNKNOWN_NODE)
        .value("DEFAULT_PARAM_NAME", adm_boost_common::DEFAULT_PARAM_NAME)
        .value("DATA_TABLE_NAME", adm_boost_common::DATA_TABLE_NAME)
        .value("DATA_PARAM_NAME", adm_boost_common::DATA_PARAM_NAME)
        .value("DATA_PARAM_VALUE", adm_boost_common::DATA_PARAM_VALUE)
        .value("MEASURE_TYPE", adm_boost_common::MEASURE_TYPE)
        .value("MEASURE_QUALIFIER", adm_boost_common::MEASURE_QUALIFIER)
        .value("MEASURE_PARAM_NAME", adm_boost_common::MEASURE_PARAM_NAME)
        .value("MEASURE_PARAM_VALUE", adm_boost_common::MEASURE_PARAM_VALUE)
        .value("VARIABLE_EXPR_OR_VALUE", adm_boost_common::VARIABLE_EXPR_OR_VALUE)
        .value("BLOCK_DELIMITER", adm_boost_common::BLOCK_DELIMITER)
        .value("CONDITIONAL_STATEMENT", adm_boost_common::CONDITIONAL_STATEMENT)
        .value("BINNED_MODEL_NAME", adm_boost_common::BINNED_MODEL_NAME)
        ;

    boost::python::class_<TSPICENetlistBoostParser>("TSPICENetlistBoostParser")
        .def("open", &TSPICENetlistBoostParser::open)
        .def("close", &TSPICENetlistBoostParser::close)
        .def("next", &TSPICENetlistBoostParser::next)
        .def("__next__", &TSPICENetlistBoostParser::next)
        .def("__iter__", pass_through)
        ;

    boost::python::class_<SpectreNetlistBoostParser>("SpectreNetlistBoostParser")
        .def("open", &SpectreNetlistBoostParser::open)
        .def("close", &SpectreNetlistBoostParser::close)
        .def("next", &SpectreNetlistBoostParser::next)
        .def("__next__", &SpectreNetlistBoostParser::next)
        .def("__iter__", pass_through)
        ;

    boost::python::class_<HSPICENetlistBoostParser>("HSPICENetlistBoostParser")
        .def("open", &HSPICENetlistBoostParser::open)
        .def("close", &HSPICENetlistBoostParser::close)
        .def("next", &HSPICENetlistBoostParser::next)
        .def("__next__", &HSPICENetlistBoostParser::next)
        .def("__iter__", pass_through)
        ;

    boost::python::class_<PSPICENetlistBoostParser>("PSPICENetlistBoostParser")
        .def("open", &PSPICENetlistBoostParser::open)
        .def("close", &PSPICENetlistBoostParser::close)
        .def("next", &PSPICENetlistBoostParser::next)
        .def("__next__", &PSPICENetlistBoostParser::next)
        .def("__iter__", pass_through)
        ;

    boost::python::class_<XyceNetlistBoostParser>("XyceNetlistBoostParser")
        .def("open", &XyceNetlistBoostParser::open)
        .def("close", &XyceNetlistBoostParser::close)
        .def("next", &XyceNetlistBoostParser::next)
        .def("__next__", &XyceNetlistBoostParser::next)
        .def("__iter__", pass_through)
        ;

}
