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


#include <boost/python.hpp>
#include <iostream>
#include <sstream>
#include <fstream>
#include <vector>
#include "rapidxml-1.13/rapidxml.hpp"
#include "rapidxml-1.13/rapidxml_print.hpp"

struct XmlLineReader {
    std::string filename;
    rapidxml::xml_document<>* doc;
    boost::python::tuple languageVersionTuple;
    boost::python::list nameLevelTupleList;
    boost::python::list unsupportedDirectiveList;
    boost::python::dict devicePropListDict;
    boost::python::dict deviceParamListDict;
    boost::python::dict directivePropListDict;
    boost::python::dict directiveParamListDict;
    boost::python::dict directiveNestedPropListDict;
    boost::python::dict modelPropListDict;
    boost::python::dict modelParamListDict;
    boost::python::dict deviceDictList;
    boost::python::dict deviceWriterTokenList;
    boost::python::dict directiveWriterTokenList;
    boost::python::dict modelWriterTokenList;
    boost::python::dict ambiguityResolutionListDict;
    boost::python::dict adminDict;

    XmlLineReader() {
        doc = new rapidxml::xml_document<>();
    }

    ~XmlLineReader() {
        delete doc;
    }


    void traverse_xml(const std::string& input_xml)
    {
        bool debug = true;
        // makes a copy of the xml - rapidxml alters it for its own purposes
        std::vector<char> xml_copy(input_xml.begin(), input_xml.end());
        xml_copy.push_back('\0');
        //rapidxml::xml_document<> doc;
        //doc.parse<rapidxml::parse_declaration_node | rapidxml::parse_no_data_nodes>(&xml_copy[0]);
        doc->parse<rapidxml::parse_declaration_node | rapidxml::parse_no_data_nodes>(&xml_copy[0]);


        /*boost::python::tuple nameLevelTuple = boost::python::make_tuple("name", "level");
          boost::python::dict deviceDict;
          deviceDict["Hello"] = 5;
          deviceDictList[nameLevelTuple] = deviceDict;*/

        rapidxml::xml_node<>* language_node=doc->first_node("language");
        std::string languageName = language_node->first_attribute("name")->value();
        std::string versionName = language_node->first_attribute("version")->value();
        languageVersionTuple =  boost::python::make_tuple(languageName, versionName);
        rapidxml::xml_node<>* devices_node=language_node->first_node("devices");

        // iterates through each device definition
        for (rapidxml::xml_node<>* cur_device_node=devices_node->first_node("device"); cur_device_node; cur_device_node=cur_device_node->next_sibling("device")) {

            // store device, level, and default attributes
            // Device/Level Key combination provides universal name for use in conversion
            std::string deviceName = cur_device_node->first_attribute("key")->value();
            std::string deviceLevel = cur_device_node->first_attribute("level")->value();
            std::string deviceLevelKey = cur_device_node->first_attribute("levelKey")->value();
            std::string deviceVersion = cur_device_node->first_attribute("version")->value();
            std::string deviceVersionKey = cur_device_node->first_attribute("versionKey")->value();
            std::string defaultAttributeValue = cur_device_node->first_attribute("default")->value();
            std::string localName = cur_device_node->first_attribute("name")->value();
            boost::python::tuple nameLevelTuple = boost::python::make_tuple(deviceName, deviceLevel, deviceLevelKey, deviceVersion, deviceVersionKey, defaultAttributeValue, localName);
            nameLevelTupleList.append(nameLevelTuple);

            // add device properties
            boost::python::list devicePropList;
            if (!add_props(cur_device_node->first_node("prop"), devicePropList, "prop"))
                std::cout << "Could not add device properties for Device: "
                    << deviceName << " Level: " << deviceLevel << std::endl;
            devicePropListDict[nameLevelTuple] = devicePropList;

            // add device params
            boost::python::list deviceParamList;
            if (!add_props(cur_device_node->first_node("param"), deviceParamList, "param"))
                std::cout << "Could not add device params for Device: "
                    << deviceName << " Level: " << deviceLevel << std::endl;
            deviceParamListDict[nameLevelTuple] = deviceParamList;

            // add ambiguity properties
            rapidxml::xml_node<>* ambiguity_node = cur_device_node->first_node("ambiguity");
            if (ambiguity_node) {
                boost::python::list ambiguityTupleList;
                for (rapidxml::xml_node<>* cur_token_node=ambiguity_node->first_node("token"); cur_token_node; cur_token_node=cur_token_node->next_sibling("token")) {

                    // order, type, label are required attributes
                    std::string order_string = cur_token_node->first_attribute("order")->value();
                    std::string type_string = cur_token_node->first_attribute("type")->value();
                    std::string label_string = cur_token_node->first_attribute("label")->value();

                    // store ambiguity tuple: (order, type, label)
                    boost::python::tuple ambiguityTuple = boost::python::make_tuple(order_string, type_string, label_string);
                    ambiguityTupleList.append(ambiguityTuple);
                }
                ambiguityResolutionListDict[nameLevelTuple] = ambiguityTupleList;
            }

            // add device writer properties
            boost::python::list deviceWriterPropList;
            rapidxml::xml_node<>* device_writer_node = cur_device_node->first_node("writer");
            if (!render_writer ( device_writer_node,
                        deviceWriterPropList )) {
                std::cout << "Instantiating the device writer failed" << std::endl;
            }

            deviceWriterTokenList[nameLevelTuple] = deviceWriterPropList;


            // add model properties
            rapidxml::xml_node<>* model_node = cur_device_node->first_node("model");

            if (model_node) {
                boost::python::list modelPropList;
                if (!add_props(model_node->first_node("prop"), modelPropList, "prop"))
                    std::cout << "Could not add model properties for Device: "
                        << deviceName << " Level: " << deviceLevel << std::endl;
                modelPropListDict[nameLevelTuple] = modelPropList;

                boost::python::list modelParamList;
                if (!add_props(model_node->first_node("param"), modelParamList, "param"))
                    std::cout << "Could not add model params for Device: "
                        << deviceName << " Level: " << deviceLevel << std::endl;
                modelParamListDict[nameLevelTuple] = modelParamList;

                // add model writer properties
                boost::python::list modelWriterPropList;
                rapidxml::xml_node<>* model_writer_node = model_node->first_node("writer");

                if (!render_writer ( model_writer_node,
                            modelWriterPropList )) {
                    std::cout << "Instantiating the model writer failed" << std::endl;
                }

                modelWriterTokenList[nameLevelTuple] = modelWriterPropList;
            }
        }


        // Add directive properties
        rapidxml::xml_node<>* directives_node=language_node->first_node("directives");

        for (rapidxml::xml_node<>* cur_directive_node=directives_node->first_node("directive"); cur_directive_node; cur_directive_node=cur_directive_node->next_sibling("directive")) {

            std::string directiveName = cur_directive_node->first_attribute("name")->value();

            if (cur_directive_node->first_attribute("unsupported"))
            {
                if (!strncmp(cur_directive_node->first_attribute("unsupported")->value(), "true", 4))
                    unsupportedDirectiveList.append(directiveName);
            }

            boost::python::list directivePropList;

            if (!add_props(cur_directive_node->first_node("prop"), directivePropList, "prop"))
                std::cout << "Could not add device properties for Directive: "  << directiveName << std::endl;
            directivePropListDict[directiveName] = directivePropList;


            boost::python::list directiveParamList;
            if (!add_props(cur_directive_node->first_node("param"), directiveParamList, "param"))
                std::cout << "Could not add device params for Directive: "
                    << directiveName << std::endl;
            directiveParamListDict[directiveName] = directiveParamList;

            // Check for possible nested directive props and handle thenm if present
            rapidxml::xml_attribute<>* nested_attribute = cur_directive_node->first_attribute("nested");
            std::string nested_string = nested_attribute ? nested_attribute->value() : "";

            if (!strncmp(nested_string.c_str(), "true", 4))
            {
                for (rapidxml::xml_node<>* cur_prop_node=cur_directive_node->first_node("prop"); cur_prop_node; cur_prop_node=cur_prop_node->next_sibling("prop"))
                {
                    rapidxml::xml_attribute<>* nested_attribute2 = cur_prop_node->first_attribute("nested");
                    std::string nested_string2 = nested_attribute2 ? nested_attribute2->value() : "";
                    if (!strncmp(nested_string2.c_str(), "true", 4))
                    {
                        std::string nestedTypeValueString = cur_prop_node->first_attribute("type")->value();
                        rapidxml::xml_node<>* nested_type_node = language_node->first_node("admin")->first_node("nestedProps")->first_node(nestedTypeValueString.c_str())->first_node("propType");

                        boost::python::list directiveNestedPropList;

                        if (!add_propTypes(nested_type_node, directiveNestedPropList))
                            std::cout << "Could not add nested properties for Directive: "  << directiveName << ", property "<< cur_prop_node->first_attribute("name") << std::endl;
                        directiveNestedPropListDict[directiveName] = directiveNestedPropList;
                    }
                }
            }

            // add directive writer properties
            boost::python::list directiveWriterPropList;
            rapidxml::xml_node<>* directive_writer_node = cur_directive_node->first_node("writer");
            if (!render_writer ( directive_writer_node,
                        directiveWriterPropList )) {
                std::cout << "Instantiating the directive writer failed" << std::endl;
            }

            directiveWriterTokenList[directiveName] = directiveWriterPropList;
        }

        // Add admin section data
        rapidxml::xml_node<>* admin_node = language_node->first_node("admin");

        // writeOptions
        boost::python::list writeOptionsList;
        rapidxml::xml_node<>* write_options_node = admin_node->first_node("writeOptions");
        rapidxml::xml_node<>* combine_print_node = write_options_node->first_node("combinePrint");

        std::string combine_print_value = combine_print_node->first_attribute("on")->value();

        std::string combinePrintString = "combinePrint";
        boost::python::tuple combine_print_tuple = boost::python::make_tuple(combinePrintString, combine_print_value);
        writeOptionsList.append(combine_print_tuple);

        rapidxml::xml_node<>* top_level_ic_node = write_options_node->first_node("topLevelIcNodeset");

        std::string top_level_ic_value = top_level_ic_node->first_attribute("on")->value();

        std::string topLevelString = "topLevelIcNodeset";
        boost::python::tuple top_level_tuple = boost::python::make_tuple(topLevelString, top_level_ic_value);
        writeOptionsList.append(top_level_tuple);

        std::string writeOptionsString = "writeOptions";
        adminDict[writeOptionsString] = writeOptionsList;

        // readOptions
        rapidxml::xml_node<>* read_options_node = admin_node->first_node("readOptions");
        rapidxml::xml_node<>* case_insensitive_node = read_options_node->first_node("caseInsensitive");

        std::string case_insensitive_value = case_insensitive_node->first_attribute("on")->value();

        std::string caseInsenstiveString = "caseInsensitive";
        boost::python::tuple case_insensitive_tuple = boost::python::make_tuple(caseInsenstiveString, case_insensitive_value);
        boost::python::list readOptionsList;
        readOptionsList.append(case_insensitive_tuple);


        rapidxml::xml_node<>* mutual_inductor_param_node = read_options_node->first_node("mutualInductorsAsParams");

        std::string mutual_inductor_param_value = mutual_inductor_param_node->first_attribute("on")->value();

        std::string mutual_inductor_param_String = "mutualInductorsAsParams";
        boost::python::tuple mutual_inductor_param_tuple = boost::python::make_tuple(mutual_inductor_param_String, mutual_inductor_param_value);

        readOptionsList.append(mutual_inductor_param_tuple);

        rapidxml::xml_node<>* store_prefix_node = read_options_node->first_node("storeDevicePrefix");

        std::string store_prefix_param_value = store_prefix_node->first_attribute("on")->value();

        std::string store_prefix_param_String = "storeDevicePrefix";
        boost::python::tuple store_prefix_param_tuple = boost::python::make_tuple(store_prefix_param_String, store_prefix_param_value);

        readOptionsList.append(store_prefix_param_tuple);


        std::string readOptionsString = "readOptions";
        adminDict[readOptionsString] = readOptionsList;

        // Title
        rapidxml::xml_node<>* title_node = admin_node->first_node("title");
        rapidxml::xml_node<>* title_writer_node = title_node->first_node("writer");

        boost::python::list titleWriterPropList;

        if (!render_writer ( title_writer_node,
                    titleWriterPropList )) {
            std::cout << "Instantiating the admininstrative title writer failed" << std::endl;
        }
        else if (debug) {
            ///std::cout << "Print contents of " << titleWriterPropList << " here." << std::endl;
            //std::cout << "Print contents of title node here." << std::endl;
        }

        std::string titleString = "title";
        adminDict[titleString] = titleWriterPropList;

        // Comment
        rapidxml::xml_node<>* comment_node = admin_node->first_node("comment");
        rapidxml::xml_node<>* comment_writer_node = comment_node->first_node("writer");

        boost::python::list commentWriterPropList;

        if (!render_writer ( comment_writer_node,
                    commentWriterPropList )) {
            std::cout << "Instantiating the admininstrative comment writer failed" << std::endl;
        }
        else if (debug) {
            //std::cout << "Print contents of comment node here." << std::endl;
        }

        std::string commentString = "comment";
        adminDict[commentString] = commentWriterPropList;

        // Inline Comment
        rapidxml::xml_node<>* inlinecomment_node = admin_node->first_node("inlinecomment");
        rapidxml::xml_node<>* inlinecomment_writer_node = inlinecomment_node->first_node("writer");

        boost::python::list inlinecommentWriterPropList;

        if (!render_writer ( inlinecomment_writer_node,
                    inlinecommentWriterPropList )) {
            std::cout << "Instantiating the admininstrative inline comment writer failed" << std::endl;
        }
        else if (debug) {
            //std::cout << "Print contents of comment node here." << std::endl;
        }

        std::string inlinecommentString = "inlinecomment";
        adminDict[inlinecommentString] = inlinecommentWriterPropList;

        // Data
        rapidxml::xml_node<>* data_node = admin_node->first_node("data");
        rapidxml::xml_node<>* data_writer_node = data_node->first_node("writer");

        boost::python::list dataWriterPropList;

        if (!render_writer ( data_writer_node,
                    dataWriterPropList )) {
            std::cout << "Instantiating the admininstrative data writer failed" << std::endl;
        }
        else if (debug) {
            ///std::cout << "Print contents of " << titleWriterPropList << " here." << std::endl;
            //std::cout << "Print contents of title node here." << std::endl;
        }

        std::string dataString = "data";
        adminDict[dataString] = dataWriterPropList;

        // Special Variables
        rapidxml::xml_node<>* specialvariables_node = admin_node->first_node("specialvariables");
        rapidxml::xml_node<>* specialvariables_writer_node = specialvariables_node->first_node("writer");

        boost::python::list specialvariablesWriterPropList;

        if (!render_writer ( specialvariables_writer_node,
                    specialvariablesWriterPropList )) {
            std::cout << "Instantiating the admininstrative special variables writer failed" << std::endl;
        }
        else if (debug) {
            //std::cout << "Print contents of comment node here." << std::endl;
        }

        std::string specialvariablesString = "specialvariables";
        adminDict[specialvariablesString] = specialvariablesWriterPropList;

        // Output Variables
        rapidxml::xml_node<>* outputvariables_node = admin_node->first_node("outputvariables");
        rapidxml::xml_node<>* outputvariables_writer_node = outputvariables_node->first_node("writer");

        boost::python::list outputvariablesWriterPropList;

        if (!render_writer ( outputvariables_writer_node,
                    outputvariablesWriterPropList )) {
            std::cout << "Instantiating the admininstrative output variables writer failed" << std::endl;
        }
        else if (debug) {
            //std::cout << "Print contents of comment node here." << std::endl;
        }

        std::string outputvariablesString = "outputvariables";
        adminDict[outputvariablesString] = outputvariablesWriterPropList;

        // measurementTypeValue
        /*rapidxml::xml_node<>* measurementTypeValue_node = admin_node->first_node("measurementTypeValue");
          rapidxml::xml_node<>* measurementTypeValue_writer_node = measurementTypeValue_node->first_node("writer");

          boost::python::list measurementTypeValueWriterPropList;

          if (!render_writer ( measurementTypeValue_writer_node,
          measurementTypeValueWriterPropList )) {
          std::cout << "Instantiating the admininstrative measurementTypeValue writer failed" << std::endl;
          }
          else if (debug) {
          std::cout << "Print contents of measurementTypeValue node here." << std::endl;
          }

          std::string measurementTypeValueString = "measurementTypeValue";
          adminDict[measurementTypeValueString] = measurementTypeValueWriterPropList;
          */
    }

    // helper functions
    bool read(std::string path) {
        filename = path;
        std::ifstream t(filename);
        if (!t.is_open()) std::cout << "Hello, Failed to open " + filename << std::endl;
        std::string str((std::istreambuf_iterator<char>(t)),
                std::istreambuf_iterator<char>());


        traverse_xml(str);
        return true;
    }

    bool render_writer (rapidxml::xml_node<> * my_model_writer_node, boost::python::list & myPropList)  {
        try
        {
            for (rapidxml::xml_node<>* cur_token_node=my_model_writer_node->first_node("token"); cur_token_node; cur_token_node=cur_token_node->next_sibling("token")) {

                boost::python::tuple myPropTuple;

                // order, type are required attributes
                std::string order_string = cur_token_node->first_attribute("order")->value();
                std::string ref_string = cur_token_node->first_attribute("ref")->value();

                // value, required, propType optional, sets to empty string if abset
                rapidxml::xml_attribute<>* value_attribute = cur_token_node->first_attribute("value");
                rapidxml::xml_attribute<>* required_attribute = cur_token_node->first_attribute("required");
                rapidxml::xml_attribute<>* label_attribute = cur_token_node->first_attribute("label");

                std::string value_string = value_attribute ? value_attribute->value() : "";
                std::string required_string = required_attribute ? required_attribute->value() : "";
                std::string label_string = label_attribute ? label_attribute->value() : "";
                // handle special type "append" - used primarily for device names
                if (ref_string == "append") {
                    boost::python::list param_list;
                    for (rapidxml::xml_node<>* cur_param_node=cur_token_node->first_node("param"); cur_param_node; cur_param_node=cur_param_node->next_sibling("param")) {
                        boost::python::tuple param_tuple;

                        //order, type, value are required attributes
                        std::string param_order_string = cur_param_node->first_attribute("order")->value();
                        std::string param_ref_string = cur_param_node->first_attribute("ref")->value();

                        rapidxml::xml_attribute<>* param_value_attribute = cur_param_node->first_attribute("value");
                        rapidxml::xml_attribute<>* param_label_attribute = cur_param_node->first_attribute("label");
                        std::string param_value_string = param_value_attribute ? param_value_attribute->value() : "";
                        std::string param_label_string = param_label_attribute ? param_label_attribute->value() : "";

                        param_tuple = boost::python::make_tuple(param_order_string, param_ref_string, param_value_string, param_label_string);
                        param_list.append(param_tuple);
                    }
                    // adding param list insteam of value string
                    myPropTuple = boost::python::make_tuple(order_string, ref_string, param_list, required_string, label_string);
                }
                else if (ref_string == "pair") {
                    // by default will include all values
                    // if includes are present, then only those included
                    // else if excludes are present, then all but excludes included
                    boost::python::list include_list, exclude_list;
                    boost::python::tuple include_exclude_tuple;
                    for (rapidxml::xml_node<>* cur_include_node = cur_token_node->first_node("include"); cur_include_node; cur_include_node = cur_include_node->next_sibling("include")) {
                        std::string include_label_string = cur_include_node->first_attribute("label")->value();
                        include_list.append(include_label_string);
                    }
                    for (rapidxml::xml_node<>* cur_exclude_node = cur_token_node->first_node("exclude"); cur_exclude_node; cur_exclude_node = cur_exclude_node->next_sibling("exclude")) {
                        std::string exclude_label_string = cur_exclude_node->first_attribute("label")->value();
                        exclude_list.append(exclude_label_string);
                    }
                    include_exclude_tuple = boost::python::make_tuple(include_list, exclude_list);
                    myPropTuple = boost::python::make_tuple(order_string, ref_string, include_exclude_tuple, required_string, label_string);

                }
                else
                {
                    myPropTuple = boost::python::make_tuple(order_string, ref_string, value_string, required_string, label_string);
                }
                myPropList.append(myPropTuple);
            }
        }
        catch (int e)
        {
            return false;
        }


        return true;
    }

    bool add_propTypes(rapidxml::xml_node<>* first_prop_node, boost::python::list& prop_list) {
        bool debug = false;
        for (rapidxml::xml_node<>* cur_prop_node=first_prop_node; cur_prop_node; cur_prop_node=cur_prop_node->next_sibling("propType")) {
            try {
                // label are required attributes
                std::string label_string = cur_prop_node->first_attribute("label")->value();

                // store propType tuple: (label, myLocalPropList )
                boost::python::tuple prop_tuple;
                boost::python::list myLocalPropList;

                // store all lower level props for this propType
                if (!add_props ( cur_prop_node->first_node("prop"),
                            myLocalPropList,
                            label_string,
                            "prop")) {
                    //std::cout << "Instantiating the admininstrative title writer failed" << std::endl;
                }
                else if (debug) {
                    ///std::cout << "Print contents of " << titleWriterPropList << " here." << std::endl;
                    //std::cout << "Print contents of title node here." << std::endl;
                }


                //prop_tuple = boost::python::make_tuple(label_string, myLocalPropList);
                prop_list.append(myLocalPropList);
            }
            catch (int e) {
                return false;
            }
        }
        return true;
    }

    bool add_props(rapidxml::xml_node<>* first_prop_node, boost::python::list& prop_list, const std::string& type_string) {

        for (rapidxml::xml_node<>* cur_prop_node=first_prop_node; cur_prop_node; cur_prop_node=cur_prop_node->next_sibling(type_string.c_str())) {
            try {
                // type, label are required attributes
                std::string type_string = cur_prop_node->first_attribute("type")->value();
                std::string label_string = cur_prop_node->first_attribute("label")->value();

                // labelKey attribute optional, sets to empty string if absent
                rapidxml::xml_attribute<>* label_key_attribute = cur_prop_node->first_attribute("labelKey");
                std::string label_key_string = label_key_attribute ? label_key_attribute->value() : "";

                // labelKey attribute optional, sets to empty string if absent
                rapidxml::xml_attribute<>* m_flag_attribute = cur_prop_node->first_attribute("mFlag");
                std::string m_flag_string = m_flag_attribute ? m_flag_attribute->value() : "";

                // value attribute optional, sets to empty string if absent
                rapidxml::xml_attribute<>* value_attribute = cur_prop_node->first_attribute("value");
                std::string value_string = value_attribute ? value_attribute->value() : "";

                // optional attribute optional, sets to empty string if absent
                rapidxml::xml_attribute<>* optional_attribute = cur_prop_node->first_attribute("optional");
                std::string optional_string = optional_attribute ? optional_attribute->value() : "";

                // nested attribute optional, sets to empty string if absent
                rapidxml::xml_attribute<>* nested_attribute = cur_prop_node->first_attribute("nested");
                std::string nested_status_string = nested_attribute ? nested_attribute->value() : "";

                // nested attribute optional, sets to empty string if absent
                rapidxml::xml_attribute<>* output_alias_attr = cur_prop_node->first_attribute("outputAlias");
                std::string output_alias_string = output_alias_attr ? output_alias_attr->value() : "";

                // store property tuple: (type, label, value, optional, nested)
                boost::python::tuple prop_tuple;
                prop_tuple = boost::python::make_tuple(type_string, label_string, label_key_string, value_string, optional_string, nested_status_string, m_flag_string, output_alias_string);
                prop_list.append(prop_tuple);
            }
            catch (int e) {
                return false;
            }
        }
        return true;
    }

    bool add_props(rapidxml::xml_node<>* first_prop_node, boost::python::list& prop_list, const std::string& opt_nested_label_str,
            const std::string& type_string) {

        for (rapidxml::xml_node<>* cur_prop_node=first_prop_node; cur_prop_node; cur_prop_node=cur_prop_node->next_sibling(type_string.c_str())) {
            try {
                // type, label are required attributes
                std::string type_string = cur_prop_node->first_attribute("type")->value();
                std::string label_string = cur_prop_node->first_attribute("label")->value();

                // labelKey attribute optional, sets to empty string if absent
                rapidxml::xml_attribute<>* label_key_attribute = cur_prop_node->first_attribute("labelKey");
                std::string label_key_string = label_key_attribute ? label_key_attribute->value() : "";

                // value attribute optional, sets to empty string if absent
                rapidxml::xml_attribute<>* value_attribute = cur_prop_node->first_attribute("value");
                std::string value_string = value_attribute ? value_attribute->value() : "";

                // optional attribute optional, sets to empty string if absent
                rapidxml::xml_attribute<>* optional_attribute = cur_prop_node->first_attribute("optional");
                std::string optional_string = optional_attribute ? optional_attribute->value() : "";

                // nested attribute optional, sets to empty string if absent
                rapidxml::xml_attribute<>* nested_attribute = cur_prop_node->first_attribute("nested");
                std::string nested_status_string = nested_attribute ? nested_attribute->value() : "";

                // store property tuple: (type, label, value, optional, nested, nested_label_value)
                boost::python::tuple prop_tuple;
                prop_tuple = boost::python::make_tuple(type_string, label_string, label_key_string, value_string, optional_string, nested_status_string, opt_nested_label_str);
                prop_list.append(prop_tuple);
            }
            catch (int e) {
                return false;
            }
        }
        return true;
    }
};

BOOST_PYTHON_MODULE(XdmRapidXmlReader)
{
    using namespace boost::python;
    class_<XmlLineReader>("XmlLineReader")
        .def("read", &XmlLineReader::read)
        .def_readonly("languageVersionTuple", &XmlLineReader::languageVersionTuple)
        .def_readonly("nameLevelTupleList", &XmlLineReader::nameLevelTupleList)
        .def_readonly("deviceDictList", &XmlLineReader::deviceDictList)
        .def_readonly("devicePropListDict", &XmlLineReader::devicePropListDict)
        .def_readonly("deviceParamListDict", &XmlLineReader::deviceParamListDict)
        .def_readonly("directivePropListDict", &XmlLineReader::directivePropListDict)
        .def_readonly("directiveParamListDict", &XmlLineReader::directiveParamListDict)
        .def_readonly("directiveNestedPropListDict", &XmlLineReader::directiveNestedPropListDict)
        .def_readonly("modelPropListDict", &XmlLineReader::modelPropListDict)
        .def_readonly("modelParamListDict", &XmlLineReader::modelParamListDict)
        .def_readonly("deviceWriterTokenList", &XmlLineReader::deviceWriterTokenList)
        .def_readonly("directiveWriterTokenList", &XmlLineReader::directiveWriterTokenList)
        .def_readonly("modelWriterTokenList", &XmlLineReader::modelWriterTokenList)
        .def_readonly("ambiguityResolutionListDict", &XmlLineReader::ambiguityResolutionListDict)
        .def_readonly("adminDict", &XmlLineReader::adminDict)
        .def_readonly("unsupportedDirectiveList", &XmlLineReader::unsupportedDirectiveList)
        ;
}
