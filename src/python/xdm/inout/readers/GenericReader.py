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


import ntpath

import xdm.inout.readers.XDMFactory as XDMFactory
from xdm import Types
from xdm.exceptions import InvalidTypeException
from xdm.inout.readers.GenericReaderState import GenericReaderState
from xdm.inout.readers.PSPICENetlistBoostParserInterface import *
from xdm.inout.readers.HSPICENetlistBoostParserInterface import *
from xdm.inout.readers.SpectreNetlistBoostParserInterface import *
from xdm.inout.xml import *
from xdm.inout.readers.ParsedNetlistLine import ParsedNetlistLine
from xdm.statements.commands import Command
from copy import deepcopy
from collections import OrderedDict

analysis_to_print_type = {".AC": "AC",
                          ".DC": "DC",
                          ".HB": "HB",
                          ".NOISE": "NOISE",
                          ".TRAN": "TRAN"
                          }


class GenericReader(object):
    """
    A generic abstract reader class for reading in netlist
    files.  Specific readers should extend this class.
    Each grammar must interface with this class.

    Member variables:
       file (os.path)

       grammar_type (flavor of grammar)

       language_definition (xml class language definition)

       grammar (grammar definition)

       reader state (keeps indexes)

    """

    def __init__(self, filename, grammar, language_definition, pspice_xml=None, spectre_xml=None, tspice_xml=None, hspice_xml=None, reader_state=None, top_reader_state=None, is_top_level_file=True, append_prefix=False, auto_translate=False, lib_sect_list=[]):
        self._file = filename

        self._grammar_type = grammar
        self._language_definition = language_definition
        self._is_top_level_file = is_top_level_file
        self._grammar = self._grammar_type(self._file, self._language_definition, self._is_top_level_file)
        self._case_insensitive = self._language_definition.is_case_insensitive()
        self._last_line = 0
        self._tspice_xml = tspice_xml
        self._pspice_xml = pspice_xml
        self._hspice_xml = hspice_xml
        self._spectre_xml = spectre_xml
        self._language_changed = False
        self._statement_count = 0
        self._append_prefix = append_prefix
        self._auto_translate = auto_translate
        self._lib_sect_list = lib_sect_list

        if not reader_state:
            self._reader_state = GenericReaderState(self._case_insensitive,
                                                    self._language_definition.is_store_device_prefix())
        else:
            self._reader_state = reader_state

        if self._is_top_level_file:
            self._top_reader_state = self._reader_state
        else:
            self._top_reader_state = top_reader_state

    @property
    def reader_state(self):
        return self._reader_state

    def read(self):
        """
        .. _reader_read:

        Iterates over an iterable grammar's component
        statements, and registers relevant components

        """
        import sys
        inc_files_and_scopes = []
        lib_files = []  # tuple list (file name, lib name)
        control_device_handling_list = []
        debug_incfiles = False
        platform = sys.platform

        grammar_iter = iter(self._grammar)
        # iterates through each grammar "line"
        for parsed_netlist_line in grammar_iter:
            self._last_line = self.read_line(parsed_netlist_line, self._reader_state, self._top_reader_state,
                                             self._language_definition, control_device_handling_list, inc_files_and_scopes, lib_files)
            self._statement_count += 1
            if self._language_changed:
                break

        # Add in default TNOM value, if not the same as Xyce's 27C
        if self._is_top_level_file and not self._grammar.tnom_defined and self._grammar.tnom_value != "27":
            parsed_netlist_line = ParsedNetlistLine(self._file, [0])
            parsed_netlist_line.type = ".OPTIONS"
            parsed_netlist_line.local_type = ".OPTIONS"
            parsed_netlist_line.add_known_object("DEVICE", Types.optionPkgTypeValue)
            parsed_netlist_line.add_param_value_pair("TNOM", self._grammar.tnom_value)
            self._last_line = self.read_line(parsed_netlist_line, self._reader_state, self._top_reader_state,
                                             self._language_definition, control_device_handling_list, inc_files_and_scopes, lib_files)

        # Add in circuit simulation temperature, if source simulator's is not the same as Xyce's 27C
        if self._is_top_level_file and not self._grammar.temp_defined and self._grammar.tnom_value != "27":
            parsed_netlist_line = ParsedNetlistLine(self._file, [0])
            parsed_netlist_line.type = ".OPTIONS"
            parsed_netlist_line.local_type = ".OPTIONS"
            parsed_netlist_line.add_known_object("DEVICE", Types.optionPkgTypeValue)
            parsed_netlist_line.add_param_value_pair("TEMP", self._grammar.tnom_value)
            self._last_line = self.read_line(parsed_netlist_line, self._reader_state, self._top_reader_state,
                                             self._language_definition, control_device_handling_list, inc_files_and_scopes, lib_files)

        # only allows for one simulator statement
        if self._language_changed:

            self._language_changed = False
            self._grammar = self._grammar_type(self._file, self._language_definition, self._is_top_level_file)
            grammar_iter = iter(self._grammar)

            # skip all lines until past simulator statement
            for i in range(self._statement_count):
                next(grammar_iter)

            for parsed_netlist_line in grammar_iter:
                self._last_line = self.read_line(parsed_netlist_line, self._reader_state, self._top_reader_state,
                                                 self._language_definition, control_device_handling_list, inc_files_and_scopes, lib_files)
                self._statement_count += 1

        logging.debug("Completed parsing file \t\"" + self._file + "\"")

        if self._auto_translate:
            # remove duplicates and re-order to favor translations involving the top
            # scope first
            inc_files_and_scopes = list(set(inc_files_and_scopes))
            if self._reader_state.scope_index.is_top_parent():
                top_inc_files_and_scopes = []
                child_inc_files_and_scopes = []
                for filename, scope in inc_files_and_scopes:
                    if scope.is_top_parent():
                        top_inc_files_and_scopes.append((filename, scope))
                    else:
                        child_inc_files_and_scopes.append((filename, scope))

                inc_files_and_scopes = []
                inc_files_and_scopes = top_inc_files_and_scopes + child_inc_files_and_scopes

            for incfile_pair in inc_files_and_scopes:
                incfile = incfile_pair[0]
                incfile_scope = incfile_pair[1]

                if debug_incfiles is True:
                    print("self._file = '%s'\n" % self._file, file=sys.stderr)
                    print("os.path.dirname(self._file) = '%s'\n" % (os.path.dirname(self._file)), file=sys.stderr)
                    print("os.path.dirname(os.path.abspath(self._file)) = '%s'\n" % (os.path.dirname(os.path.abspath(self._file))), file=sys.stderr)
                    print("incfile = '%s'\n" % incfile, file=sys.stderr)

                # incfile_resolved  = os.path.normpath(os.path.normcase(incfile)).replace('"','')
                # incfile_case_resolved  = os.path.normcase(incfile)
                incfile_case_resolved = incfile
                incfile_quote_resolved = incfile_case_resolved.replace('"', '')
                incfile_quote_resolved = incfile_quote_resolved.replace("'", '')
                incfile_path_resolved = os.path.normpath(incfile_quote_resolved)
                incfile_resolved = incfile_path_resolved
                if debug_incfiles is True:
                    print("incfile_case_resolved = '%s'\n" % incfile_case_resolved, file=sys.stderr)
                    print("incfile_quote_resolved = '%s'\n" % incfile_quote_resolved, file=sys.stderr)
                    print("incfile_path_resolved = '%s'\n" % incfile_path_resolved, file=sys.stderr)

                dirname_resolved = os.path.normpath(os.path.dirname(os.path.abspath(self._file))).replace('"', '')

                if debug_incfiles:
                    print("incfile_resolved = '%s'\n" % incfile_resolved, file=sys.stderr)
                    print("dirname_resolved = '%s'\n" % dirname_resolved, file=sys.stderr)

                if platform == "Windows":
                    if debug_incfiles:
                        print("On Windows - pre fixed file string = '%s'\n" % incfile_resolved, file=sys.stderr)
                    incfile_resolved_slashes = incfile_resolved.replace('//', '\\')
                    if debug_incfiles:
                        print("On Windows - post fixed file string = '%s'\n" % incfile_resolved, file=sys.stderr)
                else:
                    if debug_incfiles:
                        print("On Linux or OS X - pre fixed file string = '%s'\n" % incfile_resolved, file=sys.stderr)
                    incfile_resolved_slashes = incfile_resolved.replace('\\', '/')
                    if debug_incfiles:
                        print("On Linux or OS X - post fixed file string = '%s'\n" % incfile_resolved, file=sys.stderr)

                if debug_incfiles:
                    print("incfile_resolved_slashes = '%s'\n" % incfile_resolved_slashes, file=sys.stderr)

                inc_path, incfile_resolved2 = os.path.split(incfile_resolved_slashes)
                incfile_resolved3 = os.path.join(inc_path, incfile_resolved2)

                if debug_incfiles is True:
                    print("incfile2_resolved = '%s'\n" % incfile_resolved2, file=sys.stderr)
                    print("incfile3_resolved = '%s'\n" % incfile_resolved3, file=sys.stderr)

                filename = os.path.join(dirname_resolved, incfile_resolved3).replace('"', '')

                if debug_incfiles is True:
                    print("filename = '%s'\n" % filename, file=sys.stderr)

                logging.debug("Loading include file \t\t\"" + str(filename) + "\"")

                curr_scope = self._reader_state.scope_index
                self._reader_state.scope_index = incfile_scope
                include_file_reader = GenericReader(filename, self._grammar_type, self._language_definition,
                                                    reader_state=self._reader_state, top_reader_state=self._top_reader_state, 
                                                    is_top_level_file=False, tspice_xml=self._tspice_xml, pspice_xml=self._pspice_xml,
                                                    hspice_xml=self._hspice_xml, spectre_xml=self._spectre_xml, auto_translate=self._auto_translate)
                include_file_reader.read()
                self._reader_state.scope_index = curr_scope

            # re-arranges list of library filename/sections to be parsed. Originally
            # stored as a list of tuples; i.e. [(filname, sect), ... ]. Transfers
            # into an OrderedDict, with keys be the filenames and a list of library
            # sections being the dictionary entry
            lib_files_aggregated_sects = OrderedDict()
            for libfile in lib_files:
                if not libfile[0] in lib_files_aggregated_sects:
                    lib_files_aggregated_sects[libfile[0]] = []

                lib_files_aggregated_sects[libfile[0]].append(libfile[1])
             
            #read each library file/section list
            for libfile in lib_files_aggregated_sects:
                lib_file_name = libfile
                lib_names = deepcopy(lib_files_aggregated_sects[libfile])
                logging.info("Parsing Lib File: " + lib_file_name + " sections: " + ",".join(lib_names))

                filename = lib_file_name.replace("'", '').replace('"', '')

                if not os.path.isfile(filename):
                    filename = os.path.join(os.path.dirname(self._file), filename)

                library_file_reader = GenericReader(filename, self._grammar_type, self._language_definition,
                                                    reader_state=self._reader_state, top_reader_state=self._top_reader_state,
                                                    is_top_level_file=False, tspice_xml=self._tspice_xml, pspice_xml=self._pspice_xml,
                                                    hspice_xml=self._hspice_xml, spectre_xml=self._spectre_xml, auto_translate=self._auto_translate, 
                                                    lib_sect_list=lib_names)
                library_file_reader.read()

            # translate .lib files that are in child scope
            if self._is_top_level_file:
                count = 0 

                # list of .lib files in child scope may be growing ...
                while count < len(self._reader_state.lib_files_not_in_scope):
                    filename = self._reader_state.lib_files_not_in_scope[count]
                    logging.info("Parsing Lib File: " + filename)

                    library_file_reader = GenericReader(filename, self._grammar_type, self._language_definition,
                                                        reader_state=self._reader_state, top_reader_state=self._top_reader_state,
                                                        is_top_level_file=False, tspice_xml=self._tspice_xml, pspice_xml=self._pspice_xml,
                                                        hspice_xml=self._hspice_xml, spectre_xml=self._spectre_xml, auto_translate=self._auto_translate, 
                                                        lib_sect_list=[])
                    library_file_reader.read()
                    count += 1

                # library_file_reader.read_library(lib_name, control_device_handling_list, inc_files_and_scopes, lib_files)

        # unknown_pnl is a netlist line that doesn't yet know its device type
        # (e.g. spectre line that references a model of some type)
        # We loop through all the unknown pnls after the models have been read
        # and set the type and pass it back to read_line to build the device
        parent_scope = self._reader_state.scope_index
        if self._is_top_level_file:
            resolved_pnl_list = []
            for unknown_pnl, scope in self._reader_state.unknown_pnls.items():
                duplicate_pnl_flag = False
                self._reader_state.scope_index = scope
                # If MODEL_NAME is in known_objects, the unresolved device is an instantiation of
                # a user declared model, which will be resolved in first branch. The second branch is
                # for any pnl's that must be written to the top level file. The last branch is 
                # for Spectre, where the possible unresolved name is a name of a source in a directive
                language_definition = self._language_definition

                if "MODEL_NAME" in unknown_pnl.known_objects: 
                    resolved_pnl = self._reader_state.resolve_unknown_pnl(unknown_pnl, self._language_definition)

                    # If there was a language change in the file with the model card,
                    # use that language in resolving the PNL.
                    if "ST_LANG" in resolved_pnl.params_dict:
                        st_lang = resolved_pnl.params_dict.pop("ST_LANG")

                        if st_lang == self._language_definition.language:
                            pass

                        elif st_lang == "hspice":
                            xml_factory = XmlFactory(self._hspice_xml)

                        elif st_lang == "pspice":
                            xml_factory = XmlFactory(self._pspice_xml)

                        elif st_lang == "spectre":
                            xml_factory = XmlFactory(self._spectre_xml)

                        elif st_lang == "tspice":
                            xml_factory = XmlFactory(self._tspice_xml)

                        elif st_lang == "xyce":
                            xml_factory = XmlFactory(self._xyce_xml)

                        if st_lang != self._language_definition.language:
                            xml_factory.read()
                            language_definition = xml_factory.language_definition

                        if (language_definition.is_case_insensitive() and 
                            not self._reader_state.is_case_insensitive()):
                            resolved_pnl.params_dict = OrderedDict((k.upper(), v) 
                                                                   for k, v in resolved_pnl.params_dict.items())
                            resolved_pnl.known_objects = {k.upper():v 
                                                          for k, v in resolved_pnl.known_objects.items()} 

                elif unknown_pnl.flag_top_pnl:
                    resolved_pnl = unknown_pnl
                    resolved_pnl.filename = self._file
                    resolved_pnl.flag_top_pnl = False

                    # check if the top level file pnl is a duplicate. skip if it is
                    if resolved_pnl_list:
                        for prev_resolved_pnl in resolved_pnl_list:
                            match_found_flag = True

                            for key in resolved_pnl.params_dict:
                                if not key in prev_resolved_pnl.params_dict:
                                    match_found_flag = False
                                    break

                                if resolved_pnl.params_dict[key] != prev_resolved_pnl.params_dict[key]:
                                    match_found_flag = False
                                    break

                            if not match_found_flag:
                                continue

                            for key in resolved_pnl.known_objects:
                                if not key in prev_resolved_pnl.known_objects:
                                    match_found_flag = False
                                    break

                                if resolved_pnl.known_objects[key] != prev_resolved_pnl.known_objects[key]:
                                    match_found_flag = False 
                                    break

                            if match_found_flag:
                                duplicate_pnl_flag = True
                                break

                    if duplicate_pnl_flag:
                        continue

                    resolved_pnl_list.append(deepcopy(resolved_pnl))

                else:
                    resolved_pnl = self._reader_state.resolve_unknown_source(unknown_pnl, self._language_definition)

                self.read_line(resolved_pnl, self._reader_state, self._top_reader_state, language_definition,
                               control_device_handling_list, inc_files_and_scopes, lib_files)
            self._reader_state.scope_index = parent_scope

        # resolve lazy objects
        for lazy_statement_tuple in self._reader_state.scope_index.lazy_statement_index:
            for lazy_statement in lazy_statement_tuple[1]:
                for listener in lazy_statement.listener:
                    listener.resolve_lazy_bind(lazy_statement_tuple[0], lazy_statement.scope,
                                               self._reader_state.is_case_insensitive())

        # resolve control Devices
        for device, index in control_device_handling_list:
            device.resolve_control_device_list(index, self._reader_state)

        # set analysis type value of all print statements
        analysis_type = None

        if self._reader_state.scope_index.commands_index.get_statements(""):
            for statement in self._reader_state.scope_index.commands_index.get_statements(""):
                if statement.command_type in analysis_to_print_type:
                    analysis_type = analysis_to_print_type[statement.command_type]
                    break

            if analysis_type:
                for statement in self._reader_state.scope_index.commands_index.get_statements(""):
                    if statement.command_type == ".PRINT":
                        statement.set_prop(Types.analysisTypeValue, analysis_type)

            # iterate all print statements and check output variables
            if self._append_prefix:
                for statement in self._reader_state.scope_index.commands_index.get_statements(""):
                    if statement.command_type == ".PRINT":
                        variable_list = statement.get_prop(Types.outputVariableList)
                        new_list = []
                        if variable_list:
                            for variable in variable_list:
                                stripped_variable = variable[variable.find("(") + 1:variable.find(")")]
                                this_scope = parent_scope
                                colon_divided_list = stripped_variable.split(":")
                                new_colon_divided_list = []
                                for individual_variable in colon_divided_list:
                                    if this_scope.get_statement_by_name(individual_variable):
                                        this_statement = this_scope.get_statement_by_name(individual_variable)
                                        new_name = this_statement.device_type + individual_variable
                                        new_colon_divided_list.append(new_name)
                                        if this_statement.get_prop(Types.subcircuitNameValue):
                                            new_scope = this_scope.get_child_scope(
                                                this_statement.get_prop(Types.subcircuitNameValue).name)
                                            if new_scope:
                                                this_scope = new_scope
                                    else:
                                        new_colon_divided_list.append(individual_variable)
                                new_list.append(
                                    variable[:variable.find("(") + 1] + ":".join(new_colon_divided_list) + variable[
                                        variable.find(")")])
                            statement.set_prop(Types.outputVariableList, new_list)

        if self._is_top_level_file:
            parent_scope.warn_case_sensitivity()

    def read_library(self, lib_entry_name, control_device_handling_list, inc_files_and_scopes, lib_files):
        """
        .. _reader_read_library:

        Runs the reader on a library file.  Calls read(language_definition)
            for each library file.

        """
        grammar_iter = iter(self._grammar)
        read_bool = False
        for parsed_netlist_line in grammar_iter:
            if parsed_netlist_line.type == ".LIB" and parsed_netlist_line.known_objects.get(
                    Types.libEntry) == lib_entry_name:
                read_bool = True
            elif parsed_netlist_line.type == ".ENDL":
                read_bool = False
            elif read_bool:
                self.read_line(parsed_netlist_line, self._reader_state, self.top_reader_state,
                               self._language_definition, control_device_handling_list, inc_files_and_scopes, lib_files)

    @property
    def name_scope_index(self):
        """
        Gets the current NAME_SCOPE_INDEX

        Returns:
            scope index (NAME_SCOPE_INDEX)
        """
        return self._reader_state.scope_index

    @name_scope_index.setter
    def name_scope_index(self, sc):
        """
        Sets the current NAME_SCOPE_INDEX

        Args:
            sc (NAME_SCOPE_INDEX)
        """
        self._reader_state.sc = sc

    # def change_to_pspice(self):

    def read_line(self, parsed_netlist_line, reader_state, top_reader_state, language_definition, control_device_handling_list,
                  inc_files_and_scopes, lib_files):
        """
        Reads a netlist line and calls the appropriate XDMFactory method to insert the statement into the data model.
        """
        if parsed_netlist_line.flag_top_pnl:
            top_reader_state.add_unknown_pnl(parsed_netlist_line)
            
            return parsed_netlist_line.linenum[-1]

        if XDMFactory.is_supported_device(parsed_netlist_line):
            device = XDMFactory.build_device(parsed_netlist_line, reader_state, language_definition)

            if device is None:
                return parsed_netlist_line.linenum[-1]

            # handle case of preprocess directive for xyce
            if parsed_netlist_line.preprocess_keyword_value and "hspice" in language_definition.language:
                # create parsed netlist line object for the preprocess directive
                preprocess_pnl = ParsedNetlistLine(parsed_netlist_line.filename, [0])
                preprocess_pnl.type = ".PREPROCESS"
                preprocess_pnl.local_type = ".PREPROCESS"
                preprocess_pnl.add_known_object(parsed_netlist_line.preprocess_keyword_value[0].split()[0], "PREPROCESS_KEYWORD_VALUE")
                preprocess_pnl.add_value_to_value_list(parsed_netlist_line.preprocess_keyword_value[0].split()[1])

                # check if preprocess directive already in index
                preprocess_uid = -1
                for fl, objs in reader_state.scope_index.source_line_index:
                    for obj in objs:
                        last_uid = obj.uid
                        if isinstance(obj, Command):
                            if obj.command_type == ".PREPROCESS":
                                preprocess_uid = obj.uid

                # if preprocess directive not in index, add in as second index after TITLE object
                if preprocess_uid < 0:
                    XDMFactory.build_directive(preprocess_pnl, reader_state, language_definition, self._lib_sect_list)

            if device.resolve_control_devices:
                control_device_handling_list.append((device, reader_state.scope_index))
            if device.device_type == "X":
                reader_state.add_subcircuit_device(device, reader_state.scope_index)
        elif XDMFactory.is_unknown_device(parsed_netlist_line):
            reader_state.add_unknown_pnl(parsed_netlist_line)
        elif XDMFactory.is_supported_directive(parsed_netlist_line):

            # for case of standalone .PARAM statements with no actual parameters!
            if parsed_netlist_line.type == ".PARAM" and not parsed_netlist_line.params_dict:
                parsed_netlist_line.type = "COMMENT"
                parsed_netlist_line.local_type = ""
                parsed_netlist_line.name = ".PARAM"
                parsed_netlist_line.params_dict["COMMENT"] = ".PARAM"
                XDMFactory.build_comment(parsed_netlist_line, reader_state)

            # BEWARE: hack for Spectre -- takes .PARAM params from inside subckt and moves them to paramsList for subckt
            # UPDATE: 2019-06-20 -- not sure if the hack is actually needed for Spectre translation, but it seems to 
            #                       cause problems with HSPICE translation (possibly PSPICE as well). But to err on the 
            #                       side of caution, will keep code but will check input language being Spectre 
            #                       before moving into the hacked code block
            elif parsed_netlist_line.type == ".PARAM" and not reader_state.scope_index.is_top_parent() and language_definition._language.upper() == "spectre":
                reader_state.scope_index.subckt_command.set_prop(Types.subcircuitParamsList,
                                                                 parsed_netlist_line.params_dict)
            else:
                directive = XDMFactory.build_directive(parsed_netlist_line, reader_state, language_definition, self._lib_sect_list)
                if parsed_netlist_line.type == ".END":
                    reader_state.end_directive = directive
        elif parsed_netlist_line.type == ".MODEL":
            XDMFactory.build_model(parsed_netlist_line, reader_state, language_definition)
        elif parsed_netlist_line.type == ".INC" or parsed_netlist_line.type == ".INCLUDE":
            if not parsed_netlist_line.known_objects[Types.fileNameValue] in self._reader_state.master_inc_list:
                self._reader_state.add_master_inc_list(parsed_netlist_line.known_objects[Types.fileNameValue])
                self._reader_state.add_master_inc_list_scopes(reader_state.scope_index)
                inc_files_and_scopes.append((parsed_netlist_line.known_objects[Types.fileNameValue], reader_state.scope_index))
            elif parsed_netlist_line.known_objects[Types.fileNameValue] in self._reader_state.master_inc_list and reader_state.scope_index.is_top_parent():
                for ind, file_and_scope in enumerate(inc_files_and_scopes):
                    (filename, scope) = file_and_scope
                    if parsed_netlist_line.known_objects[Types.fileNameValue] == filename:
                        inc_files_and_scopes[ind] = (parsed_netlist_line.known_objects[Types.fileNameValue], reader_state.scope_index)

                inc_ind = self._reader_state.master_inc_list.index(parsed_netlist_line.known_objects[Types.fileNameValue])
                self._reader_state.master_inc_list_scopes[inc_ind] = reader_state.scope_index
                # For filenames enclosed in single quotes, ntpath doesn't seem to strip trailing
                # single quote. Therefore, will strip the single quotes before before passing
                # to ntpath.
            parsed_netlist_line.known_objects[Types.fileNameValue] = \
                ntpath.split(parsed_netlist_line.known_objects[Types.fileNameValue].replace("'", "").replace("\"", ""))[1]
            XDMFactory.build_directive(parsed_netlist_line, reader_state, language_definition, self._lib_sect_list)
        elif parsed_netlist_line.type == ".LIB":
            # Prepare lib_file name
            if parsed_netlist_line.known_objects.get(Types.fileNameValue):
                lib_file = parsed_netlist_line.known_objects[Types.fileNameValue].replace("'", '').replace('"', '')

                if not os.path.isfile(lib_file):
                    lib_file = os.path.join(os.path.dirname(self._file), lib_file)

            # Only parse .LIB statements if they are on the parent scope (the scope that 
            # includes the stuff that actually needs to be simulated). Other .LIB sections
            # are unused sections that aren't called by current simulation. This avoids
            # multiple parsing/writing of same files.
            if parsed_netlist_line.known_objects.get(Types.fileNameValue) and reader_state.scope_index.is_top_parent():

                # if .lib command calls a section within the same file, add it to list of sections to parse 
                # for the current file. otherwise, add file/section to list of libraries to be parsed later
                if os.path.normpath(self._file) == os.path.normpath(lib_file):
                    self._lib_sect_list.append(parsed_netlist_line.known_objects[Types.libEntry])
                    child = self._reader_state.scope_index.get_child_scope(parsed_netlist_line.known_objects[Types.libEntry])
                    if not child is None:
                        reader_state.scope_index.retroactive_add_statement(child)

                elif parsed_netlist_line.known_objects.get(Types.libEntry):
                    lib_files.append((parsed_netlist_line.known_objects[Types.fileNameValue],
                                      parsed_netlist_line.known_objects[Types.libEntry]))

                else:
                    lib_files.append((parsed_netlist_line.known_objects[Types.fileNameValue],
                                      parsed_netlist_line.known_objects[Types.fileNameValue]))

                if not lib_file in self._reader_state.lib_files_in_scope:
                    self._reader_state.add_lib_files_in_scope(lib_file)

                if lib_file in self._reader_state.lib_files_not_in_scope:
                    self._reader_state.remove_lib_files_not_in_scope(lib_file)

            elif parsed_netlist_line.known_objects.get(Types.fileNameValue) and not reader_state.scope_index.is_top_parent():
                # for the case of a .lib file that isn't used by the top scope, and in included 
                # by a scope outside of the top scope, the file will need to be translated. 
                # unique files (file cannot be saved more than once) are saved to a tracking list 
                # (self._lib_files_not_in_scope) to be parsed at the very end.

                # in case a library section may be added in to top scope by a .lib statement later in the file. save
                # other .lib sects included, for retroactive processing
                if os.path.normpath(self._file) == os.path.normpath(lib_file):
                    self._reader_state.scope_index.add_child_scope_lib_sects(parsed_netlist_line.known_objects[Types.libEntry])

                # for libraries added in child scope in different files
                elif os.path.normpath(self._file) != os.path.normpath(lib_file):
                    if not lib_file in self._reader_state.lib_files_not_in_scope and not lib_file in self._reader_state.lib_files_in_scope:
                        # only file name needs to be saved - the whole file is outside the top scope,
                        # so the library section doesn't matter
                        self._reader_state.add_lib_files_not_in_scope(lib_file)
             
            if parsed_netlist_line.known_objects.get(Types.fileNameValue):
                parsed_netlist_line.known_objects[Types.fileNameValue] = \
                    ntpath.split(parsed_netlist_line.known_objects[Types.fileNameValue].replace("'", "").replace("\"", ""))[1]
            XDMFactory.build_directive(parsed_netlist_line, reader_state, language_definition, self._lib_sect_list)
        elif parsed_netlist_line.type == "DATA":
            XDMFactory.build_data(parsed_netlist_line, reader_state)
        elif parsed_netlist_line.type == "TITLE":
            XDMFactory.build_title(parsed_netlist_line, reader_state)
        elif parsed_netlist_line.type == "COMMENT":
            XDMFactory.build_comment(parsed_netlist_line, reader_state)
        # spectre simulator command.  defines language type
        elif parsed_netlist_line.type == "simulator":
            lang_type = parsed_netlist_line.params_dict.get('lang')
            # for x in lang_type :
            #    # print (x)
            #    # for y in lang_type[x]:
            #        # print (y, ":", lang_type[x][y])
            # print (lang_type['lang'])
            if 'spice' in lang_type:
                logging.info("Spectre Simulator Command Found.  Switching parse mode to spice.")
                xml_factory = XmlFactory(self._hspice_xml)
                xml_factory.read()
                self._language_definition = xml_factory.language_definition
                self._grammar_type = HSPICENetlistBoostParserInterface
                self._language_changed = True
            elif 'spectre' in lang_type:
                logging.info("Spectre Simulator Command Found.  Switching parse mode to spectre.")
                xml_factory = XmlFactory(self._spectre_xml)
                xml_factory.read()
                self._language_definition = xml_factory.language_definition
                self._grammar_type = SpectreNetlistBoostParserInterface
                self._language_changed = True
        else:
            logging.error("Unable to parse line: " + str(parsed_netlist_line.linenum))
            raise InvalidTypeException()

        return parsed_netlist_line.linenum[-1]
