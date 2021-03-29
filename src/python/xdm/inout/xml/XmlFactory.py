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

from xdm.inout.xml.XmlDeviceModel import XmlDeviceModel
from xdm.inout.xml.XmlDeviceParam import XmlDeviceParam
from xdm.inout.xml.XmlDeviceToken import XmlDeviceToken
from xdm.inout.xml.XmlDeviceType import XmlDeviceType
from xdm.inout.xml.XmlDirectiveType import XmlDirectiveType
from xdm.inout.xml.XmlLanguageDefinition import XmlLanguageDefinition
from xdm.inout.xml.XmlParam import XmlParam
from xdm.inout.xml.XmlProp import XmlProp
from xdm.inout.xml.XmlWriter import XmlWriter

import XdmRapidXmlReader


class XmlIgnoreParamList(object):
    def __init__(self, name_list):
        self.name_list = name_list


class XmlFactory(object):
    """
    Creates an XMLLanguageDefinition.

    Member variables:
        xml_file (string of file name for xml definition)

        reader (XmlLineReader)

        language_definition (XmlLanguageDefinition)

        directiveList (list of directives...does not look like it gets used)
    """
    def __init__(self, xml_file=None):
        self._xml_file = xml_file
        self._reader = XdmRapidXmlReader.XmlLineReader()
        self._language_definition = None
        # TODO: Figure out whether we can get rid of self._directiveList
        self._directiveList = []

    def create_devices(self, case_insensitive):
        """
        Iterates over each device name-level tuple, which contains all props and params associated with the
        name-level tuple.  Also iterates writers and models.

        :param case_insensitive: bool whether language is case insensitive
        :return:
        """
        for nameLevelTuple in self._reader.nameLevelTupleList:
            # tuple: Device Name, Device Level, Device level (global) Key, Device Default Attribute, Device local name
            if case_insensitive:
                newDevice = XmlDeviceType(nameLevelTuple[0].upper(), nameLevelTuple[1], nameLevelTuple[2].upper(), nameLevelTuple[3], nameLevelTuple[4].upper(), nameLevelTuple[5], nameLevelTuple[6].upper())
            else:
                newDevice = XmlDeviceType(nameLevelTuple[0], nameLevelTuple[1], nameLevelTuple[2], nameLevelTuple[3], nameLevelTuple[4], nameLevelTuple[5], nameLevelTuple[6])

            for propTuple in self._reader.devicePropListDict[nameLevelTuple]:
                newProp = XmlProp(propTuple[0], propTuple[1], propTuple[2], propTuple[3], output_alias=propTuple[7])
                newDevice.add_prop(newProp)

            for paramTuple in self._reader.deviceParamListDict[nameLevelTuple]:
                newParam = XmlParam(paramTuple[0], paramTuple[1], paramTuple[2], paramTuple[3], paramTuple[6])
                newDevice.add_param(newParam)

            device_writer = create_writer(self._reader.deviceWriterTokenList, nameLevelTuple)
            newDevice.writer = device_writer

            ambiguity_token_list = []
            if self._reader.ambiguityResolutionListDict.get(nameLevelTuple):
                for token in self._reader.ambiguityResolutionListDict.get(nameLevelTuple):
                    newToken = XmlDeviceToken(token[0], token[1], token[2], None, None)
                    ambiguity_token_list.append(newToken)
            newDevice.ambiguity_token_list = ambiguity_token_list

            if self._reader.modelPropListDict.get(nameLevelTuple):
                newModel = XmlDeviceModel()
                for modelPropTuple in self._reader.modelPropListDict[nameLevelTuple]:
                    newModelProp = XmlProp(modelPropTuple[0], modelPropTuple[1], modelPropTuple[2], modelPropTuple[3])
                    newModel.add_prop(newModelProp)
                for modelParamTuple in self._reader.modelParamListDict[nameLevelTuple]:
                    newModelParam = XmlParam(modelParamTuple[0], modelParamTuple[1], modelParamTuple[2], modelParamTuple[3])
                    newModel.add_param(newModelParam)
                newDevice.model = newModel
                newModel.device_type = newDevice
                model_writer = create_writer(self._reader.modelWriterTokenList, nameLevelTuple)
                newModel.writer = model_writer
            self._language_definition.add_device_type(newDevice)

    @property
    def language_definition(self):
        return self._language_definition

    def create_directives(self, case_insensitive):
        """
        Iterates over each directive tuple, which contains all props and params associated with the
        directive

        :param case_insensitive: bool whether language is case insensitive
        :return:
        """

        for directive in self._reader.directivePropListDict:
            newDirective = XmlDirectiveType(directive)
            self._directiveList.append(newDirective)
            for propTuple in self._reader.directivePropListDict[directive]:
                newProp = XmlProp(propTuple[0], propTuple[1], propTuple[2], propTuple[3])
                newDirective.add_prop(newProp)

            for paramTuple in self._reader.directiveParamListDict[directive]:
                newParam = XmlParam(paramTuple[0], paramTuple[1], paramTuple[2], paramTuple[3])
                newDirective.add_param(newParam)

            # Check for nested Directive existance
            if directive in self._reader.directiveNestedPropListDict:
                newDirective.nested = True
                for nestedPropTuple in self._reader.directiveNestedPropListDict[directive]:
                    for innerPropTuple in nestedPropTuple:
                        newProp = XmlProp(innerPropTuple[0], innerPropTuple[1], innerPropTuple[2], innerPropTuple[3])
                        newProp.nested = True
                        newProp.nested_propType = innerPropTuple[6]
                        newDirective.add_nested_prop(innerPropTuple[6], newProp)

            directive_writer = create_writer(self._reader.directiveWriterTokenList, directive)
            newDirective.writer = directive_writer

            self._language_definition.add_directive_type(newDirective)

        self._language_definition.unsupported_directive_list = self._reader.unsupportedDirectiveList

    def create_admin(self):
        """
        Sets 'admin' params writeOptions and readOptions to define language-specific traits, like case sensitivity,
        print directive combination, or other language-specific quirks.  Hacks in the code may access these admin
        properties to see whether a hack should be applied.

        :return:
        """
        adminDict = {}
        for item in self._reader.adminDict:
            if item in ['title', 'comment', 'inlinecomment', 'data', 'specialvariables', 'outputvariables']:
                writer = create_writer(self._reader.adminDict, item)
                adminDict[item] = writer
            elif item in ['writeOptions']:
                adminDict['writeOptions'] = self._reader.adminDict['writeOptions']
            elif item in ['readOptions']:
                adminDict['readOptions'] = self._reader.adminDict['readOptions']

        self._language_definition.admin_dict = adminDict

    def read(self):
        """
        Base-level read for XML language.  Calls other functions in this class.

        :return:
        """
        self._reader.read(self._xml_file)
        case_insensitive = False
        for read_option in self._reader.adminDict['readOptions']:
            if read_option[0] == "caseInsensitive":
                case_insensitive = (read_option[1].lower() == "true")
            if read_option[0] == "storeDevicePrefix":
                store_device_prefix = (read_option[1].lower() == "true")
        self._language_definition = XmlLanguageDefinition(self._reader.languageVersionTuple[0], self._reader.languageVersionTuple[1], case_insensitive, store_device_prefix)
        self.create_devices(case_insensitive)
        self.create_directives(case_insensitive)
        self.create_admin()

    @property
    def xml_file(self):
        return self._xml_file

    @xml_file.setter
    def xml_file(self, xml_file):
        self._xml_file = xml_file

    def print_language_def(self):
        for device_type in self._language_definition.device_types:
            device_type.print_me()


def create_writer(writerTokenList, nameLevelTuple):
    """
    Creates writer token by token (XmlDeviceToken).

    :param writerTokenList:
    :param nameLevelTuple:
    :return:
    """
    token_list = []
    for token in writerTokenList[nameLevelTuple]:
        newToken = None
        if (token[1] == "append"):
            device_param_list = []
            for param_tuple in token[2]:
                device_param = XmlDeviceParam(param_tuple[0], param_tuple[1], param_tuple[2], param_tuple[3])
                device_param_list.append(device_param)
            newToken = XmlDeviceToken(token[0], token[1], device_param_list, token[3], token[4])
        else:
            newToken = XmlDeviceToken(token[0], token[1], token[2], token[3], token[4])
        token_list.append(newToken)
    xml_writer = XmlWriter(token_list)
    return xml_writer
