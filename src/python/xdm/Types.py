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


# Defines the name of the statement (if exists)
name = "MY_NAME"

# statement type for use in indexes
# name-scope for node is different than device name-scope
statementType = "STATEMENT_TYPE"

deviceName = "DEVICE_NAME"
directiveName = "DIRECTIVE_NAME"
modelType = "MODEL_TYPE"
modelName = "MODEL_NAME"
vbicModel = "VBIC_MODEL"
vbicModelName = "VBIC_MODEL_NAME"
controlDeviceName = "CONTROL_DEVICE_NAME"
controlDeviceList = "CONTROL_DEVICE_LIST"
acValue = "AC_VALUE"
acMagValue = "AC_MAG_VALUE"
acPhaseValue = "AC_PHASE_VALUE"
dcValue = "DC_VALUE"
dcValueValue = "DC_VALUE_VALUE"
transient = "TRANSIENT"

PValue = "P_VALUE"
BValue = "B_VALUE"
TValue = "T_VALUE"
digDevType = "DIG_DEV_TYPE"

libEntry = "LIB_ENTRY"

controlType = "CONTROL_TYPE"
control = "CONTROL"

posNodeName = "POS_NODE_NAME"
negNodeName = "NEG_NODE_NAME"
anodeNodeName = "ANODE_NAME"
posControlNodeName = "POSCONTROLNODE_NAME"
negControlNodeName = "NEGCONTROLNODE_NAME"
drainNodeName = "DRAINNODE_NAME"
gateNodeName = "GATENODE_NAME"
sourceNodeName = "SOURCENODE_NAME"
collectorNodeName = "COLLLECTORNODE_NAME"
baseNodeName = "BASENODE_NAME"
emitterNodeName = "EMITTERNODE_NAME"
collectorPrimeNodeName = "COLLECTORPRIMENODE_NAME"
basePrimeNodeName = "BASEPRIMENODE_NAME"
emitterPrimeNodeName = "EMITTERPRIMENODE_NAME"
posSwitchNodeName = "POSSWITCHNODE_NAME"
negSwitchNodeName = "NEGSWITCHNODE_NAME"
aPortPosNodeName = "APORTPOSNODE_NAME"
aPortNegNodeName = "APORTNEGNODE_NAME"
bPortPosNodeName = "BPORTPOSNODE_NAME"
bPortNegNodeName = "BPORTNEGNODE_NAME"
substrateNodeName = "SUBSTRATENODE_NAME"
thermalNodeName = "THERMALNODE_NAME"
temperatureNodeName = "TEMPERATURENODE_NAME"
lowOutputNodeName = "LOWOUTPUTNODE_NAME"
highOutputNodeName = "HIGHOUTPUTNODE_NAME"
inputReferenceNodeName = "INPUTREFERENCENODE_NAME"
inputNodeName = "INPUTNODE_NAME"
outputNodeName = "OUTPUTNODE_NAME"
accelerationNodeName = "ACCELERATIONNODE_NAME"
velocityNodeName = "VELOCITYNODE_NAME"
positionNodeName = "POSITIONNODE_NAME"
generalNodeName = "GENERAL_NODE"
externalBodyContactNodeName = "EXTERNALBODYCONTACTNODE_NAME"
internalBodyContactNodeName = "INTERNALBODYCONTACTNODE_NAME"
node_list = "NODE_LIST"
standalone_param = "STANDALONE_PARAM"
dataTableName = "DATA_TABLE_NAME"

tempValue = "TEMP_VALUE"
couplingValue = "COUPLING_VALUE"
areaValue = "AREA_VALUE"
funcNameArgValue = "FUNCNAMEARG_VALUE"
funcBodyValue = "FUNCBODY_VALUE"
fileNameValue = "FILENAME_VALUE"
entryNameValue = "ENTRYNAME_VALUE"
calcTypeValue = "CALCTYPE_VALUE"
analysisTypeValue = "ANALYSISTYPE_VALUE"
resultNameValue = "RESULT_NAME_VALUE"
outputVariableValue = "OUTPUTVARIABLE_VALUE"
optionPkgTypeValue = "OPTION_PKG_TYPE_VALUE"
keywordValue = "KEYWORD_VALUE"
printStepValue = "PRINTSTEP_VALUE"
finalTimeValue = "FINALTIME_VALUE"
startTimeValue = "STARTTIME_VALUE"
stepCeilingValue = "STEPCEILING_VALUE"
noOpValue = "NOOP_VALUE"
uicValue = "UIC_VALUE"
controlDeviceValue = "CONTROLDEVICE_VALUE"
onOffValue = "ONOFF_VALUE"
gainValue = "GAIN_VALUE"
transconductanceValue = "TRANSCONDUCTANCE_VALUE"
measurementValue = "MEASUREMENT_VALUE"
measurementTypeValue = "MEASUREMENT_TYPE_VALUE"
outputValue = "OUTPUT_VALUE"
sweepTypeValue = "SWEEP_TYPE_VALUE"
pointsValue = "POINTS_VALUE"
startFreqValue = "START_FREQ_VALUE"
endFreqValue = "END_FREQ_VALUE"
generalValue = "GENERAL_VALUE"
fundFreqValue = "FUND_FREQ_VALUE"
freqValue = "FREQ_VALUE"
funcArgValue = "FUNC_ARG_VALUE"
funcNameValue = "FUNC_NAME_VALUE"
funcArgList = "FUNC_ARG_LIST"
funcExpression = "FUNC_EXPRESSION"
preprocessKeywordValue = "PREPROCESS_KEYWORD_VALUE"
scheduleValue = "SCHEDULE_VALUE"
scheduleParamValue = "SCHEDULE_PARAM_VALUE"
scheduleType = "SCHEDULE_TYPE"
sweepParamValue = "SWEEP_PARAM_VALUE"
sweep = "SWEEP"

restOfLine = "REST_OF_LINE"


subcircuitNameValue = "SUBCIRCUITNAME_VALUE"

valueList = "VALUE_LIST"
outputVariableList = "OUTPUTVARIABLE_LIST"
nodeList = "NODE_LIST"
interfaceNodeList = "INTERFACE_NODE_LIST"
controlNodeList = "CONTROL_NODE_LIST"
initialConditionsList = "INITIAL_CONDITIONS_LIST"

measureType = "MEASURE_TYPE"
measureQualifier = "MEASURE_QUALIFIER"
measureParamName = "MEASURE_PARAM_NAME"
measureParamValue = "MEASURE_PARAM_VALUE"
variableExprValue = "VARIABLE_EXPR_OR_VALUE"


polyParamValue = "POLY_PARAM_VALUE"
controlParamValue = "CONTROL_PARAM_VALUE"
subcktDirectiveParamValue = "SUBCKT_DIRECTIVE_PARAM_VALUE"
subcktDeviceParamValue = "SUBCKT_DEVICE_PARAM_VALUE"

tableParamValue = "TABLE_PARAM_VALUE"
list_param_value = "LIST_PARAM_VALUE"
poly_value = "POLY_VALUE"

poly = "POLY"
polyExpression = "POLY_EXPRESSION"
params = "PARAMS"
value = "VALUE"
model = "MODEL"
sweep_list = "SWEEP_LIST"
table = "TABLE"
tableExpression = "TABLE_EXPRESSION"
valueExpression = "VALUE_EXPRESSION"
controlExpression = "CONTROL_EXPRESSION"
paramsList = "PARAMS_LIST"
subcircuitParamsList = "SUBCIRCUIT_PARAMS_LIST"

valueKeyword = "VALUE_KEYWORD"

lazyObject = "LAZY_OBJECT"


# need to rename/reorganize
trans_func = "TRANS_FUNC"
trans_ref = "TRANS_REF"
expression = "EXPRESSION"
voltage = "VOLTAGE"
current = "CURRENT"
voltageOrCurrent = "VOLTAGE_OR_CURRENT"
paramsHeader = "PARAMSHEADER"
comment = "COMMENT"
title = "TITLE"
