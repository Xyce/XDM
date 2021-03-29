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


import logging
from xdm.index import NAME_SCOPE_INDEX
from xdm.statements.nodes.models import MASTER_MODEL
from xdm.statements.nodes.devices import Device
from copy import deepcopy


class GenericReaderState(object):
    """
    Keeps the name scope index, devices, and nodes.  Used for reference
    within XDMFactory
    """
    def __init__(self, case_insensitive=False, store_device_prefix=False):
        self._sc = NAME_SCOPE_INDEX()
        self._devices = []
        self._nodes = {}
        self._unknown_pnls = {}
        self._subcircuit_device = {}
        self._case_insensitive = case_insensitive
        self._store_device_prefix = store_device_prefix
        self._end_directive = None
        self._pwl_files = []

        # used to track .lib files in the top scope and those not in the top scope. 
        # those not in the top scope will eventually need to be translated as well.
        self._lib_files_in_scope = []
        self._lib_files_not_in_scope = []
        # used to track .inc files that have already been flagged for translation
        self._master_inc_list = []
        self._master_inc_list_scopes = []

    def add_unknown_pnl(self, pnl):
        self._unknown_pnls[pnl] = self._sc

    @property
    def unknown_pnls(self):
        return self._unknown_pnls

    @property
    def scope_index(self):
        """
        Gets the current NAME_SCOPE_INDEX

        Returns:
            scope index (NAME_SCOPE_INDEX)
        """
        return self._sc

    @scope_index.setter
    def scope_index(self, sc):
        """
        Gets the current NAME_SCOPE_INDEX

        Returns:
            scope index (NAME_SCOPE_INDEX)
        """
        self._sc = sc

    def set_modelDef(self, pnl, modelDef):
        """
        Sets the model Def info in the PNL object

        Returns:
            pnl (ParsedNetlistLine)
        """
        pnl.type = modelDef.device_type
        pnl.local_type = modelDef.device_local_type

        # TODO fix device level keys in XDMFactory.build_device
        pnl.add_param_value_pair("LEVEL", modelDef.device_level)
        if modelDef.device_version:
            pnl.add_param_value_pair("VERSION", modelDef.device_version)

        pnl.flag_unresolved_device = False

        return

    def resolve_unknown_pnl(self, pnl, language_definition):

        # could be resolving model defined after device instantiation
        # could be resolving SUBCKT in spectre -- ambiguous
        model_key = pnl.known_objects["MODEL_NAME"]
        if self._case_insensitive:
            model_key = model_key.upper()

        modelDef = ""
        for key in self._sc.statements:
            st = self._sc.statements[key]

            if isinstance(st, MASTER_MODEL):
                for m in st.models:
                    modelName = m.name
                    if self._case_insensitive:
                        modelName = modelName.upper()
                    if model_key == modelName:
                        modelDef = m
                        self.set_modelDef(pnl, modelDef)
                        return pnl

                    # check if binned model by checking the root part of the name. 
                    # use the first declaration's definition
                    if modelName.startswith(model_key + "."):
                        modelDef = m
                        self.set_modelDef(pnl, modelDef)
                        return pnl

        # if model definition not found in current scope, check scopes of include files
        if not modelDef:
            for scope in self._master_inc_list_scopes:
                statements = scope.statements

                for key in statements:
                    st = statements[key]

                    if isinstance(st, MASTER_MODEL):
                        for m in st.models:
                            modelName = m.name
                            if self._case_insensitive:
                                modelName = modelName.upper()
                            if model_key == modelName:
                                modelDef = m
                                pnl.model_def_scope = scope
                                self.set_modelDef(pnl, modelDef)
                                return pnl

                            # check if binned model by checking the root part of the name. 
                            # use the first declaration's definition
                            if modelName.startswith(model_key + "."):
                                modelDef = m
                                pnl.model_def_scope = scope
                                self.set_modelDef(pnl, modelDef)
                                return pnl

        # for Spectre. first check children to see if subckt definition exists for device
        for child_scope in self._sc.children:
            if model_key == child_scope.subckt_command.name:
                pnl.type = "X"
                pnl.local_type = "inline subcircuit"
                pnl.subckt_device_param_list = pnl.unknown_nodes
                pnl.unknown_nodes = []
                pnl.add_subckt_device_param_value(model_key)  # mimic Xyce param list
                pnl.flag_unresolved_device = False
                return pnl

        # for Spectre. next, check parent's children (aka, subckts in same scope
        # as current subckt) if subckt definition exists for device 
        if self._sc.parent is not None:
            for child_scope in self._sc.parent.children:
                if model_key == child_scope.subckt_command.name:
                    pnl.type = "X"
                    pnl.local_type = "inline subcircuit"
                    pnl.subckt_device_param_list = pnl.unknown_nodes
                    pnl.unknown_nodes = []
                    pnl.add_subckt_device_param_value(model_key)  # mimic Xyce param list
                    pnl.flag_unresolved_device = False
                    return pnl

        # pdb.set_trace()
        if pnl.type != "X" and not "SPECTRE" in language_definition._language:
            logging.warning("Line(s):" + str(pnl.linenum) 
                + ". Could not resolve unknown device " + model_key + ", model not found in scope. Using default model type.")

            return pnl
        else:
            raise Exception("Could not resolve unknown device, model not found in scope")

    def resolve_unknown_source(self, pnl, language_definition):

        # For Spectre, to resolve source names in directives. Since sources are renamed
        # in Spectre translations based on the type (voltage or current source), the new 
        # name needs to be reflected in directives that use that source
        if self._case_insensitive:
            model_key = model_key.upper()

        for key in self._sc.statements:
            st = self._sc.statements[key]

            if isinstance(st, Device):
                if st.name == pnl.sweep_param_list[0]:
                    pnl.sweep_param_list[0] = st.device_type+pnl.sweep_param_list[0]

        pnl.flag_unresolved_device = False

        return pnl

    def add_subcircuit_device(self, subcircuit_device, scope):
        # print "adding device", subcircuit_device.props
        # if not self._subcircuit_device.get(scope):
        #     self._subcircuit_device[scope] = []
        self._subcircuit_device[subcircuit_device] = scope

    def is_case_insensitive(self):
        return self._case_insensitive

    def is_store_device_prefix(self):
        return self._store_device_prefix

    @property
    def end_directive(self):
        return self._end_directive

    @end_directive.setter
    def end_directive(self, end_directive):
        self._end_directive = end_directive

    def add_pwl_file(self, pwl_file):
        self._pwl_files.append(pwl_file)

    @property
    def pwl_files(self):
        return self._pwl_files

    def add_lib_files_in_scope(self, lib_file):
        self._lib_files_in_scope.append(lib_file)

    @property
    def lib_files_in_scope(self):
        return self._lib_files_in_scope

    def add_lib_files_not_in_scope(self, lib_file):
        self._lib_files_not_in_scope.append(lib_file)

    def remove_lib_files_not_in_scope(self, lib_file):
        self._lib_files_not_in_scope.remove(lib_file)

    @property
    def lib_files_not_in_scope(self):
        return self._lib_files_not_in_scope

    def add_master_inc_list(self, inc_file):
        self._master_inc_list.append(inc_file)

    @property
    def master_inc_list(self):
        return self._master_inc_list

    def add_master_inc_list_scopes(self, scope):
        self._master_inc_list_scopes.append(scope)

    @property
    def master_inc_list_scopes(self):
        return self._master_inc_list_scopes
