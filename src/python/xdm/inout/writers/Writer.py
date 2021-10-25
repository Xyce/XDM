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

from copy import deepcopy
import logging
import ntpath
import os

from xdm import Types
from xdm.exceptions import NotImplementedException
from xdm.inout.writers.writer_utils import *
from xdm.inout.xml import XmlFactory, XmlDeviceToken
from xdm.statements import Statement
from xdm.statements.commands import Command
from xdm.statements.nodes.devices.Device import Device
from xdm.statements.nodes.models.modeldefs import ModelDef
from xdm.statements.refs import TITLE, COMMENT, DATA
from xdm.statements.structures.SWEEP import SWEEP, DATA_SWEEP, LIN_SWEEP


class Writer(object):
    """ A generic writer class for writing out netlist
        files.  The constructor takes in a list of supported
        types for writing. For example:

        :Example:
            .. code-block:: python

                T = (XyceCAPACITOR, XyceRESISTOR, XyceBJT)
                W = Writer('temp.txt', T)

                # We assume I is a UID_INDEX created earlier
                W.write_objects(I)

        This example writes out an internal data model.  This
        file will only support XyceCAPACITOR, XyceRESISTOR, and
        XyceBJT meaning any other devices will not be written.
        The UID_INDEX was created when the data model was read in.

        The writer also has support for logging.  Logging allows
        any errors or warnings to be written to an output (file,
        command line, socket, etc...).  An example:

        :Example:
            .. code-block:: python

                T = (XyceCAPACITOR, XyceRESISTOR)
                L = FileLogger('somefile.txt')
                W = Writer('temp.txt', T, L)

                # We assume I is a UID_INDEX created earlier
                W.write_objects(I)

        Let's assume the index included XyceBJT.  In this instance
        we do not support the object (only XyceCAPACITOR and
        XyceRESISTOR) and an error will get written to the Logger.
    """

    def __init__(self, dir_name, xml_lang_file, input_language_definition, log=None, combine_off=False):
        """
        Args:
           dir_name (str): Output dir (full path)

           xml_lang_file (str): Full path to XML file defining the output language
        """
        self._cur_file_path = None

        if isinstance(dir_name, str):
            self._dir_name = dir_name
            self._f = None
        else:
            self._dir_name = None
            self._f = dir_name
        self.log = log

        self._output_language_factory = XmlFactory(xml_lang_file)
        self._output_language = self._output_language_factory.language_definition
        self._input_language_factory = input_language_definition
        self._input_language = input_language_definition

        self._combine_off = combine_off
        # construct mapping of abstract data model classes to grammar classes
        self._construct_map_dict()

        self._cur_line = 1


    @property
    def input_language(self):
        return self._input_language

    @property
    def output_language(self):
        return self._output_language

    @property
    def options_list_aggregate(self):
        return self._options_list_aggregate

    def _construct_map_dict(self):
        self._output_language_factory.read()
        self._output_language = self._output_language_factory.language_definition

        self._device_dict = {}

        self._device_writer = {}
        self._model_writer = {}
        for device_type in self._output_language_factory.language_definition.device_types:
            self._device_writer[device_type.device_level_key] = device_type.writer.token_list
            if device_type.model:
                self._model_writer[device_type.device_level_key] = device_type.model.writer

        self._directive_writer = {}
        for directive_type in self._output_language_factory.language_definition.directive_types:
            self._directive_writer[directive_type.name] = directive_type.writer.token_list

        self._admin_writer = self._output_language_factory.language_definition.admin_dict

        # several of the unit tests erroneously passes in a XmlFactory object into input_language_definition
        # instead of the actual input language definition. this checks whether this is the case, and gets
        # the input_langage_definition in that case.
        if isinstance(self._input_language, XmlFactory):
            self._input_language_factory.read()
            self._input_language = self._input_language_factory.language_definition

        # if input_language_definition not given at all (as in some instances of the unit tests), then
        # _input_admin_writer is set to _admin_writer. if not, then get the admin_dict
        if self._input_language is not None:
            self._input_admin_writer = self._input_language.admin_dict
        else:
            self._input_admin_writer = deepcopy(self._admin_writer)

        # enables storing .PRINT statements
        self._output_variable_list_aggregate = {}
        self._output_variable_list_line = 0
        self._output_variable_list_analysis_type = ""
        self._final_line_num = {}
        self._combine_print_flag = False

        self._options_list_aggregate = {}
        self._options_last_file = None
        self._combine_options_flag = False
        self._options_last_line_num = 0

        self._temperature_list_aggregate = {}
        self._temperature_final_line_num = {}

        if not self._combine_off:
            for option in self._admin_writer["writeOptions"]:
                if option[0] == "combinePrint":
                    self._combine_print_flag = option[1] == "true"

    def _write_line(self, ws, xdm_version, from_version, to_version):
        """ Writes a line to the file.  This is a protected
        function call and should only be called by children
        of the Writer class (such as XyceWriter).

        This function appends a line separator to the end of each line.
        The line separator is specific to the operating system, such
        as '\n' for linux and '\r\n' for windows.

        Args:
            ws
            xdm_version
            from_version
            to_version

        """
        # Update files if new file and we know directory
        if (self._cur_file_path is None or not ntpath.basename(self._cur_file_path) == ntpath.basename(ws.file)) and self._dir_name is not None:

            if ws.file is None or 1 > len(ws.file):
                logging.error('Object at ' + ws.line_num[0] + ' : ' + ws + ' has no file attributed.')
                raise Exception('*****FATAL ERROR*****')

            # Reset file paths
            self._cur_file_path = os.path.join(self._dir_name, ntpath.basename(ws.file))

            # print "RRL debug: Writer:136 self._cur_file_path opened for wb = " + self._cur_file_path + ", ws.get_file = " + ws.file

            self._f = open(self._cur_file_path, 'wb')

            self.write_version(xdm_version, from_version, to_version)
            # Reset file line
            self._cur_line = 5

        ret_str = ''

        d = []
        lang = None
        can_convert_special_var = True
        can_translate_output_var = True
        unsupported_output_vars = []

        _iaw_sp = self._input_admin_writer['specialvariables']
        _aw_sp = self._admin_writer['specialvariables']
        _iaw_ov = self._input_admin_writer['outputvariables']
        _aw_ov = self._admin_writer['outputvariables']
        _process_sp = self._process_specials

        self._options_last_file = ws.file

        if isinstance(ws, Device):
            results = _process_sp(ws, _iaw_sp, _aw_sp, specialvariable=True)
            can_convert_special_var, unsupported_var, conflicting_var = [i for i in results]
            d = self._device_writer[ws.device_level_key]
            lang = self._output_language.get_device_by_name_level_key(ws.device_level_key, ws.device_version_key)

            # match existing params to new params
            self.check_params(ws)

        elif isinstance(ws, TITLE):
            d = self._admin_writer['title'].token_list

        elif isinstance(ws, COMMENT):
            d = self._admin_writer['comment'].token_list

        elif isinstance(ws, DATA):
            d = self._admin_writer['data'].token_list

        elif isinstance(ws, Command):
            lang = self._output_language.get_directive_by_name(ws.command_type)


            if ws.command_type != ".OPTIONS":
                results = _process_sp(ws, _iaw_sp, _aw_sp, specialvariable=True)
                can_convert_special_var, unsupported_var, conflicting_var = [i for i in results]

            if self._combine_print_flag and ws.command_type in ['.PRINT', '.PROBE', '.PROBE64'] and can_convert_special_var:
                results = _process_sp(ws, _iaw_ov, _aw_ov, outputvariable=True)
                can_translate_output_var, unsupported_output_vars = [i for i in results]

                if can_translate_output_var:
                    output_file = self._set_output_file(ws, output_variable=True)

                    for output_variable in ws.get_prop(Types.outputVariableList):
                        self._output_variable_list_aggregate[(ws.file, output_file)].append((output_variable, ws.line_num))
                    self._output_variable_list_line = self._cur_line
                    if ws.get_prop(Types.analysisTypeValue):
                        self._output_variable_list_analysis_type = ws.get_prop(Types.analysisTypeValue).upper()
                else:
                    d = self._directive_writer[ws.command_type]

            elif ws.command_type == ".OPTIONS" and can_convert_special_var:
                option_package = ws.get_prop(Types.optionPkgTypeValue)

                if not self._options_list_aggregate.get(option_package):
                    self._options_list_aggregate[option_package] = {}

                for key, val in ws.get_prop(Types.paramsList).items():
                    self._options_list_aggregate[option_package][key] = val
                    self._options_last_line_num = self._cur_line

            elif (ws.command_type == ".TEMP" or ws.command_type == ".TEMPERATURE") and can_convert_special_var:
                # Aggregate all the .TEMP statements before writing out
                # Output statement will depend on the output language and whether one or more 
                # .TEMP statements are present.
                output_file = self._set_output_file(ws, temperature=True)

                for temperature in ws.get_prop(Types.valueList):
                    self._temperature_list_aggregate[(ws.file, output_file)].append(temperature)

            else:
                if ws.command_type in self._output_language_factory.language_definition.unsupported_directive_list:
                    oline = "In file:'%s' at line:%s. Unsupported type: %s. Retained (as a comment). Continuing."
                    logging.warning(oline % (str(os.path.basename(ws.file)), str(ws.line_num), ws.command_type))

                if ws.command_type in ['.PRINT', '.PROBE', '.PROBE64'] and can_convert_special_var:
                    results = _process_sp(ws, _iaw_ov, _aw_ov, outputvariable=True)
                    can_translate_output_var, unsupported_output_vars = [i for i in results]

                d = self._directive_writer[ws.command_type]

        elif isinstance(ws, ModelDef):
            d = self._model_writer[ws.device_level_key].token_list[:]
            level_token = XmlDeviceToken(999, "model_level", self._output_language_factory.language_definition.get_device_by_name_level_key(ws.device_level_key, ws.device_version_key).device_level, None, None)
            d.append(level_token)
            lang = self._output_language.get_device_by_name_level_key(ws.device_level_key, ws.device_version_key).model
            self.check_params(ws, is_model=True)

        else:
            return

        # Code to handle special variables that cannot be converted
        if not can_convert_special_var:
            # Case of special variable with no equivalent in target language
            if unsupported_var:
                oline = "In file:'%s' at line:%s. Expression contains unsupported special variable: %s. XDM Retained (as a comment). Continuing."
                logging.warning(oline % (str(os.path.basename(ws.file)), str(ws.line_num), unsupported_var))
                ret_str += self._admin_writer['comment'].token_list[0].value[0].value

            # Case of variable name conflicting with name of special variable in target language
            # 2019-10-04 : conflicting variable names now just replace with "XYCE_*", will not be commented out
            elif conflicting_var:
                for var in conflicting_var:
                    oline = "In file:'%s' at line:%s. Expression contains variable that conflicts with a special variable in target language: %s. XDM Retained (as a comment). Continuing."
                    logging.warning(oline % (str(os.path.basename(ws.file)), str(ws.line_num), var))

                    # for the case of the parameter name conflicting with special variable in Xyce,
                    # replace the parameter name with "XYCE_*" 
                    original_keys_to_be_deleted = []

                    for key in ws.props:
                        if key == "PARAMS_LIST" or key == "SUBCIRCUIT_PARAMS_LIST":
                            for param_key in ws.props[key]:
                                if param_key.lower() == var.lower():
                                    original_keys_to_be_deleted.append((key, param_key))

                    for key, param_key in original_keys_to_be_deleted:
                        ws.props[key]["XYCE_"+param_key.upper()] = ws.props[key][param_key]
                        del ws.props[key][param_key]

        # Code to handle unsupported output variables
        if not can_translate_output_var:
            for unsupported_output_var in unsupported_output_vars:
                oline = "In file:'%s' at line:%s. Expression contains unsupported output variable: %s. XDM Retained (as a comment). Continuing."
                logging.warning(oline % (str(os.path.basename(ws.file)), str(ws.line_num), unsupported_output_var))

            ret_str += self._admin_writer['comment'].token_list[0].value[0].value

        cur_length = 0

        for field in d:
            try:
                r = eval(field.ref)(field, ws, d, lang)

                line_count = 0

                if (field.label == "outputVariableList" and 
                    "xyce.xml" in to_version and 
                    "*" in r and can_convert_special_var):
                    r_fields = r.split()
                    new_r = ""

                    for ind, r_field in enumerate(r_fields):
                        isExpression = self._is_expression(r_field)

                        if "*" in r_field and not "V(*)" in r_field.upper() and not isExpression:
                            oline = "Line(s):%s. Unsupported Output Variable in Xyce: %s"
                            logging.warning(oline % (str(self._cur_line+line_count), str(r_field)))

                            if "\n" in r_field:
                                new_r += "\n"

                        else:
                            if ind == 0:
                                new_r += r_field

                            else:
                                new_r += " "+r_field

                        if "\n" in r_field:
                            line_count += 1

                    r = new_r

                self._cur_line += r.count("\n")

            except AttributeError as e:
                oline = "Object at %s : %s Field: %s gave: %s"
                logging.error(oline % (str(ws.line_num[0]), str(ws), str(field), e.message))

                raise Exception('*****FATAL ERROR*****')

            if 0 < len(r):
                # doing our best to keep char count under 80 per line
                if cur_length > 0 and (cur_length + len(r)) > 80:
                    if ret_str[0] == self._admin_writer['comment'].token_list[0].value[0].value:
                        ret_str += '\n* '
                        self._cur_line += 1
                    elif not r.startswith("\n+"):
                        ret_str += '\n+ '
                        self._cur_line += 1
                    cur_length = 0
                ret_str += r + ' '
                cur_length += len(r) + 1

        if not can_convert_special_var:
            if unsupported_var:
                ret_str += "; XDM Retained (as a comment). Continuing."

        # handle inline comment
        # inline comments can make line greater than 80 chars
        if ws.inline_comment is not None:
            # Checks if line will be aggregated. If so, the inline comment is put on it's own line, so
            # it will be commented out as a regular comment. If not, it will be commented out with 
            # the language specific inline comment character.
            if not d:
                inline_comment_tokens = self._admin_writer['comment'].token_list
            else:
                inline_comment_tokens = self._admin_writer['inlinecomment'].token_list
            ret_str = ret_str.strip() + handle_inline_comment(ws, inline_comment_tokens, lang)

        # self._cur_line incremented at end of function
        ret_str = ret_str.strip() + '\n'

        # writing an extra line to make space for "Converted using XDM..."
        if self._cur_line < (ws.line_num[0] + 4):
            for i in range(self._cur_line, (ws.line_num[0] + 4)):
                ret_str += '\n'
                self._cur_line += 1

        ret_str_not_coded = ret_str
        ret_str = ret_str.encode('ascii', 'ignore')

        try:
            ret_str_encoded = ret_str_not_coded.encode('utf-8')
            ret_str_decoded = ret_str_encoded.decode('ascii')
            self._f.write(ret_str)
        except UnicodeDecodeError as e:
            if isinstance(ws, COMMENT):
                import string
                printable = set(string.printable)
                filtered = ""
                filtered = filtered.join(list(filter(lambda x: x in printable, list(ret_str_not_coded))))
                self._f.write(filtered.encode('utf-8'))

                oline = "Non-ASCII character detected in the comment within file '%s' at line number(s) %s"
                logging.warning(oline % (str(os.path.basename(ws.file)), str(ws.line_num)))

            else:
                oline = "Could not convert non-ASCII character(s) within file '%s' at line number(s) %s"
                logging.error(oline % (str(os.path.basename(ws.file)), str(ws.line_num)))

                raise Exception('Unicode Decode Error')

        self._cur_line += 1

    def _process_specials(self, ws, iaw, aw, specialvariable=False, outputvariable=False):
        """ Checks if special variables in expressions and
        output variables can be processed.

        Args:
            ws
            iaw
            aw
            specialvariable
            outputvariable

        """

        _iaw = self._input_admin_writer
        _aw = self._admin_writer
        _setup_sp_dict = setup_special_variable_dicts
        _handle_sp = handle_special_variables
        _handle_ov = handle_output_variables

        target_lang_conflict_dict, source_lang_specials_dict = _setup_sp_dict(iaw, aw)

        if specialvariable:
            results = _handle_sp(ws, target_lang_conflict_dict, source_lang_specials_dict, _iaw, _aw)

        elif outputvariable:
            results = _handle_ov(ws, target_lang_conflict_dict, source_lang_specials_dict)

        return results

    def _is_expression(self, item):
        """ Checks if input has been determined to be an expression,
        as indicated by being enclosed in single quotes or curly 
        braces.

        Args:
            item

        """

        if ((item.startswith("'") and item.endswith("'")) or 
            (item.startswith("{") and item.endswith("}"))):
            return True
        
        else:
            return False

    def _set_output_file(self, ws, temperature=False, output_variable=False):
        """ Checks if writable statement is associated with a 
        particular file. Returns that file, or "XDEFAULTX" if 
        not. Initializes lists for output aggregation for that
        particular file.

        Args:
            ws

        """

        output_file = ws.get_prop("FILE")

        if not output_file:
            output_file = "XDEFAULTX"

        if temperature:
            self._temperature_final_line_num[(ws.file, output_file)] = self._cur_line 

            if not self._temperature_list_aggregate.get((ws.file, output_file)):
                self._temperature_list_aggregate[(ws.file, output_file)] = []

        elif output_variable:
            self._final_line_num[(ws.file, output_file)] = ws.line_num

            if not self._output_variable_list_aggregate.get((ws.file, output_file)):
                self._output_variable_list_aggregate[(ws.file, output_file)] = []

        return output_file

    def combine_print(self, to_version):
        for print_aggregate_file in self._output_variable_list_aggregate:
            print_directive = Command({}, {}, "GENERATED", [-1], -1)
            print_directive.command_type = ".PRINT"

            print_directive.set_prop(Types.analysisTypeValue, self._output_variable_list_analysis_type)

            if print_aggregate_file[1] == "XDEFAULTX":
                print_directive.add_param("FORMAT", "PROBE")

            else:
                print_directive.add_param("FILE", print_aggregate_file[1])
            print_directive.set_prop(Types.outputVariableList, self.clean_output_variable_list(self._output_variable_list_aggregate[print_aggregate_file], to_version, self._final_line_num[print_aggregate_file]))

            self._cur_file_path = os.path.join(self._dir_name, ntpath.basename(print_aggregate_file[0]))

            directive_writer = self._directive_writer[".PRINT"]

            return_string = self.build_output_line(print_directive, directive_writer, self._output_language.get_directive_by_name(".PRINT"))

            return_string += " ; aggregated using xdm"

            return_string = return_string.encode('utf-8')

            with open(self._cur_file_path, 'rb') as original_file:

                original_lines = original_file.readlines()
                original_lines.insert(self._output_variable_list_line, return_string + "\n".encode('utf-8'))

                # NOTE: the code in the comments should be logging.warning, if it's ever uncommented
                # TODO: remove the commented out code below once it's deemed not helpful/informational
                # superseded by bug fix for Bugzilla 2023
                # if "XYCE" in to_version.upper() and "*" in return_string:
                #     logging.warn("Writing line that will not work in Xyce. Output line " + str(self._output_variable_list_line + 1))
                #     logging.warn("File: " + str(self._cur_file_path))
                #     logging.warn("Line text: " + return_string)

            with open(self._cur_file_path, 'wb') as altered_file:
                altered_file.writelines(original_lines)

    def clean_output_variable_list(self, in_list, to_version, line_num):
        out_list = []

        for item in in_list:
            # Check if * is in an delimited expression. If it is in delimited expression, it's allowed.
            # If not, it is a wildcard and not allowed.
            isExpression = self._is_expression(item[0])

            if not isExpression:
                if ("xyce.xml" in to_version and "*" in item[0] and 
                    not "V(*)" in ''.join(item[0].split()).upper()):
                    oline = "Line(s):%s. Unsupported Output Variable in Xyce: %s"
                    logging.warning(oline % (str(item[1]), str(item[0])))

                    continue

            out_list.append(item[0])

        if "xyce.xml" in to_version and not out_list:
            oline = "Line(s):%s Writing .PRINT line with no variables.  Replacing with V(*)"
            logging.warning(oline % str(line_num))

            out_list.append("V(*)")

        return out_list

    def combine_options(self, to_version):
        lines_to_add = []
        for option_type in self._options_list_aggregate:
            options_directive = Command({}, {}, "GENERATEDOPTIONS", [self._options_last_line_num], -1)
            options_directive.command_type = ".OPTIONS"

            this_params_list = self._options_list_aggregate[option_type]
            options_directive.set_prop(Types.paramsList, this_params_list)
            options_directive.set_prop(Types.optionPkgTypeValue, option_type)

            if self._options_last_file is None or 1 > len(self._options_last_file):
                logging.error('During combine_options : Object at ' + str(self._options_last_line_num) + ' has no file attributed.')
                raise Exception('*****FATAL ERROR*****')

            self._cur_file_path = os.path.join(self._dir_name, ntpath.basename(self._options_last_file))

            directive_writer = self._directive_writer[".OPTIONS"]

            return_string = self.build_output_line(options_directive, directive_writer, self._output_language.get_directive_by_name(".OPTIONS"))

            return_string += " ; converted options using xdm" + "\n"
            return_string = return_string.encode('utf-8')
            lines_to_add.append(return_string)

        with open(self._cur_file_path, 'rb') as original_file:

            original_lines = original_file.readlines()
            original_lines[self._options_last_line_num:self._options_last_line_num] = lines_to_add


        with open(self._cur_file_path, 'wb') as altered_file:
            altered_file.writelines(original_lines)

    def combine_temperatures(self, to_version):
        for aggregate_file in self._temperature_list_aggregate:

            self._cur_file_path = os.path.join(self._dir_name, ntpath.basename(aggregate_file[0]))

            # If no temperature present, special variable TEMP is used,  and the output language is Xyce,
            # use special processing for single output .STEP statement
            if "xyce.xml" in to_version and len(self._temperature_list_aggregate[aggregate_file]) == 1:
                directive = Command({}, {}, "GENERATED", [-1], -1)
                directive.command_type = ".TEMP"
                directive.set_prop(Types.valueList, self._temperature_list_aggregate[aggregate_file])
                
                directive_writer = self._directive_writer[".TEMP"]

                return_string = self.build_output_line(directive, directive_writer, self._output_language.get_directive_by_name(".TEMP"))

            # If output language is Xyce and more .TEMP statement present,
            # use special processing for different output (.STEP with a .DATA table)
            elif "xyce.xml" in to_version and len(self._temperature_list_aggregate[aggregate_file]) > 1:
                sweep_obj = SWEEP()
                data_sweep = DATA_SWEEP("XDMgeneratedTable")
                sweep_obj.add_sweep(data_sweep)

                directive = Command({}, {}, "GENERATED", [-1], -1)
                directive.command_type = ".STEP"
                directive.set_prop(Types.sweep, sweep_obj)

                directive_writer = self._directive_writer[".STEP"]

                return_string = ""
                ret_str = self.build_output_line(directive, directive_writer, self._output_language.get_directive_by_name(".STEP"))
                return_string += ret_str + "\n"

                directive = Command({}, {}, "GENERATED", [-1], -1)
                directive.command_type = ".DATA"

                directive.set_prop(Types.valueList, ["temp"])

                directive.set_prop(Types.dataTableName, "XDMgeneratedTable")

                directive_writer = self._directive_writer[".DATA"]

                ret_str = self.build_output_line(directive, directive_writer, self._output_language.get_directive_by_name(".DATA"))
                return_string += ret_str

                for temperature in self._temperature_list_aggregate[aggregate_file]:
                    directive = DATA({}, "GENERATED", [-1], -1)


                    directive.set_prop(Types.valueList, [temperature])

                    directive_writer = self._admin_writer["data"].token_list

                    ret_str = self.build_output_line(directive, directive_writer, None)
                    return_string += ret_str

                directive = Command({}, {}, "GENERATED", [-1], -1)
                directive.command_type = ".ENDDATA"

                directive_writer = self._directive_writer[".ENDDATA"]

                ret_str = self.build_output_line(directive, directive_writer, self._output_language.get_directive_by_name(".ENDDATA"))
                return_string += "\n" + ret_str

            # For output into a simulator language other than Xyce, use normal XML
            # schema for output. Placeholder code, to be modified if needed in future.
            elif not "xyce.xml" in to_version:
                directive = Command({}, {}, "GENERATED", [-1], -1)
                directive.command_type = ".TEMP"
                directive.set_prop(Types.valueList, self._temperature_list_aggregate[aggregate_file])
                
                directive_writer = self._directive_writer[".TEMP"]

                return_string = self.build_output_line(directive, directive_writer, self._output_language.get_directive_by_name(".TEMP"))

            return_string = return_string.encode('utf-8')

            with open(self._cur_file_path, 'rb') as original_file:

                original_lines = original_file.readlines()
                original_lines.insert(self._temperature_final_line_num[aggregate_file], return_string + "\n".encode('utf-8'))

            with open(self._cur_file_path, 'wb') as altered_file:
                altered_file.writelines(original_lines)

            return

    def write_objects(self, wss, xdm_version, from_version, to_version):
        """ Writes a list of WritableStatements to the file.
        Typically, we would create a writer (say XyceWriter),
        then pass an enumeration from the index of WritableStatements.
        Internally, this will call write_object() on
        each statement.

        Args:
           wss (Enum of WritableStatements): Enum of WritableStatement
                                            that is written to file
        """
        for ws in wss:
            self.write_object(ws, xdm_version, from_version, to_version)
        self._f.close()

        if self._combine_print_flag:
            self.combine_print(to_version)
        self.combine_options(to_version)
        self.combine_temperatures(to_version)

    def write_object(self, ws, xdm_version, from_version, to_version):
        """ Writes a WritableStatement to the file.  Typically,
        we would create a writer (say XyceWriter), then enumerate
        the index of WritableStatements and call write_object() on
        each statement. We can also call write_objects with an
        enumeration of WritableStatements

        This function MUST be overridden by implementing class

        Args:
           ws (WritableStatement): WritableStatement that is written to file
        """
        if self.can_write(ws):
            self._write_line(ws, xdm_version, from_version, to_version)
        else:
            raise NotImplementedException(str(self.__class__) + " does not support " +
                                          str(ws.__class__))

    def can_writes(self, wss):
        """ Check to see if we can writes a list of WritableStatements
        to the file.  Typically, we would create a writer (say XyceWriter),
        then pass an enumeration from the index of WritableStatements.
        Internally, this will call can_write() on each statement.

        Args:
           wss (Enum of WritableStatements): Enum of WritableStatements that is written to file

        Returns:
           bool.  True if we can write the list, false if not
        """
        for ws in wss:
            if not self.can_write(ws):
                return False

        return True

    def can_write(self, ws):
        """ Check to see if we can write a WritableStatement
        to the file.  Typically, we would create a writer (say XyceWriter),
        then pass each WritableStatement.

        Args:
           ws (WritableStatement): WritableStatement that is written to file

        Returns:
           bool.  True if we can write the statement, false if not
        """

        if isinstance(ws, Device):
            return ws.device_level_key in self._device_writer
        else:
            return isinstance(ws, Statement)

    def write_version(self, xdm_version, from_version, to_version):
        import time
        converted_string = "** Translated using xdm "
        converted_string += xdm_version
        converted_string += " on "
        converted_string += time.strftime("%b_%d_%Y_%H_%M_%S_%p")
        converted_string += "\n** from "
        converted_string += from_version
        converted_string += "\n** to "
        converted_string += to_version
        converted_string += "\n\n"
        self._f.write(converted_string.encode('utf-8'))

    def check_params(self, obj, is_model=False):
        device_type = self._output_language.get_device_by_name_level_key(obj.device_level_key)
        oline_model_param = "\n\t\t\t\t\tIn file '%s' (%s)\n\t\t\t\t\tAt line number %s, param '%s' does not exist\n\t\t\t\t\tin the target language (%s) for device/level '%s'. Continuing and writing param '%s' anyway."
        oline_inst_param = "\n\t\t\t\t\tIn file '%s' (%s)\n\t\t\t\t\tAt line number %s, param '%s' does not exist\n\t\t\t\t\tin the target language (%s) for device/level '%s'. Removing param '%s'."
        removal_list = []

        if is_model:

            model_type = device_type.model

            for param in obj.params:

                if not model_type.key_params.get(param):

                    removal_list.append(param)
                    logging.info(oline_model_param % (str(os.path.basename(obj.file)),
                                          str(self.input_language.language), str(obj.line_num),
                                          str(param), str(self.output_language.language),
                                          str(device_type.levelKey), str(param)))

        else:

            for param in obj.params:

                if not device_type.key_params.get(param):

                    removal_list.append(param)
                    logging.info(oline_inst_param % (str(os.path.basename(obj.file)),
                                          str(self.input_language.language), str(obj.line_num),
                                          str(param), str(self.output_language.language),
                                          str(device_type.levelKey), str(param)))

            for param in removal_list:

                del obj.params[param]

    def build_output_line(self, obj, writer, output_language_get_directive_by_name):
        return_string = ""
        
        for field in writer:
            try:
                r = eval(field.ref)(field, obj, writer, output_language_get_directive_by_name)

            except AttributeError as e:
                oline = "Object %s Field: %s gave: %s"
                logging.error(oline % (str(obj), str(field), e.message))

                raise Exception('*****FATAL ERROR*****')

            if 0 < len(r):
                if r.endswith("\n"):
                    return_string += r

                else:
                    return_string += r + ' '

        return return_string
