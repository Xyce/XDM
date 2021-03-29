#-------------------------------------------------------------------------
#   Copyright 2002-2020 National Technology & Engineering Solutions of
#   Sandia, LLC (NTESS).  Under the terms of Contract DE-NA0003525 with
#   NTESS, the U.S. Government retains certain rights in this software.
#
#   This file is part of the Xyce(TM) XDM Netlist Translator.
#   
#   Xyce(TM) XDM is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#  
#   Xyce(TM) XDM is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#   
#   You should have received a copy of the GNU General Public License
#   along with the Xyce(TM) XDM Netlist Translator.
#   If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------


import SpiritCommon
import xdm.Types as Types

# Maps Boost Spirit types with xdm Types
boost_xdm_map_dict = {SpiritCommon.data_model_type.DIRECTIVE_NAME: Types.name,
                      SpiritCommon.data_model_type.DEVICE_NAME: Types.name,
                      SpiritCommon.data_model_type.MODEL_NAME: Types.modelName,
                      SpiritCommon.data_model_type.MODEL_TYPE: Types.modelType,
                      SpiritCommon.data_model_type.POSNODE: Types.posNodeName,
                      SpiritCommon.data_model_type.NEGNODE: Types.negNodeName,
                      SpiritCommon.data_model_type.PARAM_VALUE: Types.value,
                      SpiritCommon.data_model_type.VALUE: Types.value,
                      SpiritCommon.data_model_type.GATENODE: Types.gateNodeName,
                      SpiritCommon.data_model_type.SOURCENODE: Types.sourceNodeName,
                      SpiritCommon.data_model_type.DRAINNODE: Types.drainNodeName,
                      SpiritCommon.data_model_type.TRANS_FUNC_TYPE: Types.trans_func,
                      SpiritCommon.data_model_type.TRANS_REF_NAME: Types.trans_ref,
                      SpiritCommon.data_model_type.ANODE: Types.anodeNodeName,
                      SpiritCommon.data_model_type.POSCONTROLNODE: Types.posControlNodeName,
                      SpiritCommon.data_model_type.NEGCONTROLNODE: Types.negControlNodeName,
                      SpiritCommon.data_model_type.COLLECTORNODE: Types.collectorNodeName,
                      SpiritCommon.data_model_type.BASENODE: Types.baseNodeName,
                      SpiritCommon.data_model_type.EMITTERNODE: Types.emitterNodeName,
                      SpiritCommon.data_model_type.COLLECTORPRIMENODE: Types.collectorPrimeNodeName,
                      SpiritCommon.data_model_type.BASEPRIMENODE: Types.basePrimeNodeName,
                      SpiritCommon.data_model_type.EMITTERPRIMENODE: Types.emitterPrimeNodeName,
                      SpiritCommon.data_model_type.POSSWITCHNODE: Types.posSwitchNodeName,
                      SpiritCommon.data_model_type.NEGSWITCHNODE: Types.negSwitchNodeName,
                      SpiritCommon.data_model_type.APORTPOSNODE: Types.aPortPosNodeName,
                      SpiritCommon.data_model_type.APORTNEGNODE: Types.aPortNegNodeName,
                      SpiritCommon.data_model_type.BPORTPOSNODE: Types.bPortPosNodeName,
                      SpiritCommon.data_model_type.BPORTNEGNODE: Types.bPortNegNodeName,
                      SpiritCommon.data_model_type.SUBSTRATENODE: Types.substrateNodeName,
                      SpiritCommon.data_model_type.TEMPERATURENODE: Types.temperatureNodeName,
                      SpiritCommon.data_model_type.LOWOUTPUTNODE: Types.lowOutputNodeName,
                      SpiritCommon.data_model_type.HIGHOUTPUTNODE: Types.highOutputNodeName,
                      SpiritCommon.data_model_type.INPUTREFERENCENODE: Types.inputReferenceNodeName,
                      SpiritCommon.data_model_type.INPUTNODE: Types.inputNodeName,
                      SpiritCommon.data_model_type.OUTPUTNODE: Types.outputNodeName,
                      SpiritCommon.data_model_type.ACCELERATIONNODE: Types.accelerationNodeName,
                      SpiritCommon.data_model_type.VELOCITYNODE: Types.velocityNodeName,
                      SpiritCommon.data_model_type.POSITIONNODE: Types.positionNodeName,
                      SpiritCommon.data_model_type.GENERALNODE: Types.generalNodeName,
                      SpiritCommon.data_model_type.EXTERNALBODYCONTACTNODE: Types.externalBodyContactNodeName,
                      SpiritCommon.data_model_type.INTERNALBODYCONTACTNODE: Types.internalBodyContactNodeName,
                      SpiritCommon.data_model_type.EXPRESSION: Types.expression,
                      SpiritCommon.data_model_type.VOLTAGE: Types.voltage,
                      SpiritCommon.data_model_type.CURRENT: Types.current,
                      SpiritCommon.data_model_type.PARAMS_HEADER: Types.paramsHeader,
                      SpiritCommon.data_model_type.ON: Types.onOffValue,
                      SpiritCommon.data_model_type.OFF: Types.onOffValue,
                      SpiritCommon.data_model_type.COMMENT: Types.comment,
                      SpiritCommon.data_model_type.FILENAME: Types.fileNameValue,
                      SpiritCommon.data_model_type.TITLE: Types.title,
                      SpiritCommon.data_model_type.CONTROL_DEVICE: Types.controlDeviceValue,
                      SpiritCommon.data_model_type.OPTION_PKG_TYPE_VALUE: Types.optionPkgTypeValue,
                      SpiritCommon.data_model_type.CONTROL_DEV_VALUE: Types.controlDeviceValue,
                      SpiritCommon.data_model_type.ANALYSIS_TYPE: Types.analysisTypeValue,
                      SpiritCommon.data_model_type.OUTPUT_VARIABLE: Types.outputVariableValue,
                      SpiritCommon.data_model_type.VALUE_KEYWORD: Types.valueKeyword,
                      SpiritCommon.data_model_type.GAIN_VALUE: Types.gainValue,
                      SpiritCommon.data_model_type.TRANSCONDUCTANCE_VALUE: Types.transconductanceValue,
                      SpiritCommon.data_model_type.VBIC_MODEL: Types.vbicModel,
                      SpiritCommon.data_model_type.VBIC_MODEL_NAME: Types.vbicModelName,
                      SpiritCommon.data_model_type.THERMALNODE: Types.thermalNodeName,
                      SpiritCommon.data_model_type.AREA_VALUE: Types.areaValue,
                      SpiritCommon.data_model_type.TABLE: Types.table,
                      SpiritCommon.data_model_type.LIST_PARAM_VALUE: Types.list_param_value,
                      SpiritCommon.data_model_type.POLY: Types.poly,
                      SpiritCommon.data_model_type.POLY_VALUE: Types.poly_value,
                      SpiritCommon.data_model_type.CONTROL_DEVICE_NAME: Types.controlDeviceName,
                      SpiritCommon.data_model_type.INLINE_COMMENT: Types.comment,
                      SpiritCommon.data_model_type.PRINT_STEP_VALUE: Types.printStepValue,
                      SpiritCommon.data_model_type.FINAL_TIME_VALUE: Types.finalTimeValue,
                      SpiritCommon.data_model_type.START_TIME_VALUE: Types.startTimeValue,
                      SpiritCommon.data_model_type.STEP_CEILING_VALUE: Types.stepCeilingValue,
                      SpiritCommon.data_model_type.COUPLING_VALUE: Types.couplingValue,
                      SpiritCommon.data_model_type.DC_VALUE: Types.dcValue,
                      SpiritCommon.data_model_type.DC_VALUE_VALUE: Types.dcValueValue,
                      SpiritCommon.data_model_type.AC_VALUE: Types.acValue,
                      SpiritCommon.data_model_type.AC_MAG_VALUE: Types.acMagValue,
                      SpiritCommon.data_model_type.AC_PHASE_VALUE: Types.acPhaseValue,
                      SpiritCommon.data_model_type.LIB_ENTRY: Types.libEntry,
                      SpiritCommon.data_model_type.TABLE_PARAM_VALUE: Types.tableParamValue,
                      SpiritCommon.data_model_type.POLY_PARAM_VALUE: Types.polyParamValue,
                      SpiritCommon.data_model_type.CONTROL_PARAM_VALUE: Types.controlParamValue,
                      SpiritCommon.data_model_type.SUBCKT_DIRECTIVE_PARAM_VALUE: Types.subcktDirectiveParamValue,
                      SpiritCommon.data_model_type.SUBCKT_DEVICE_PARAM_VALUE: Types.subcktDeviceParamValue,
                      SpiritCommon.data_model_type.SWEEP_TYPE: Types.sweepTypeValue,
                      SpiritCommon.data_model_type.POINTS_VALUE: Types.pointsValue,
                      SpiritCommon.data_model_type.START_FREQ_VALUE: Types.startFreqValue,
                      SpiritCommon.data_model_type.END_FREQ_VALUE: Types.endFreqValue,
                      SpiritCommon.data_model_type.GENERAL_VALUE: Types.generalValue,
                      SpiritCommon.data_model_type.FUND_FREQ_VALUE: Types.fundFreqValue,
                      SpiritCommon.data_model_type.FREQ_VALUE: Types.freqValue,
                      SpiritCommon.data_model_type.FUNC_ARG_VALUE: Types.funcArgValue,
                      SpiritCommon.data_model_type.FUNC_NAME_VALUE: Types.funcNameValue,
                      SpiritCommon.data_model_type.FUNC_EXPRESSION: Types.funcExpression,
                      SpiritCommon.data_model_type.PREPROCESS_KEYWORD: Types.preprocessKeywordValue,
                      SpiritCommon.data_model_type.NOOP_VALUE: Types.noOpValue,
                      SpiritCommon.data_model_type.UIC_VALUE: Types.uicValue,
                      SpiritCommon.data_model_type.SCHEDULE_TYPE: Types.scheduleType,
                      SpiritCommon.data_model_type.SCHEDULE_PARAM_VALUE: Types.scheduleParamValue,
                      SpiritCommon.data_model_type.SWEEP_PARAM_VALUE: Types.sweepParamValue,
                      SpiritCommon.data_model_type.TEMP_VALUE: Types.tempValue,
                      SpiritCommon.data_model_type.REST_OF_LINE: Types.restOfLine,
                      SpiritCommon.data_model_type.DIG_DEV_TYPE: Types.digDevType,
                      SpiritCommon.data_model_type.CONTROL: Types.control,
                      SpiritCommon.data_model_type.RESULT_NAME_VALUE: Types.resultNameValue,
                      SpiritCommon.data_model_type.MEASURE_TYPE: Types.measureType,
                      SpiritCommon.data_model_type.MEASURE_QUALIFIER: Types.measureQualifier,
                      SpiritCommon.data_model_type.MEASURE_PARAM_NAME: Types.measureParamName,
                      SpiritCommon.data_model_type.MEASURE_PARAM_VALUE: Types.measureParamValue,
                      SpiritCommon.data_model_type.VARIABLE_EXPR_OR_VALUE: Types.variableExprValue,
                      SpiritCommon.data_model_type.DATA_TABLE_NAME: Types.dataTableName
                      }
