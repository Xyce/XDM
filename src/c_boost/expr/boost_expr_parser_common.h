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


#if !defined(EXPR_BOOOST_COMMON)
#define EXPR_BOOOST_COMMON

#include <boost/config/warning_disable.hpp>
#include <boost/spirit/include/qi.hpp>
#include <boost/spirit/include/phoenix_core.hpp>
#include <boost/spirit/include/phoenix_operator.hpp>
#include <boost/spirit/include/phoenix_fusion.hpp>
#include <boost/spirit/include/phoenix_stl.hpp>
#include <boost/spirit/include/phoenix_object.hpp>

#include <vector>
#include <iostream>

namespace expr_boost_common 
{
    enum expr_data_model_type
    {
        ADD, BUILTIN_CONST, BUILTIN_FUNC, DIVIDE, EQUALITY, EQUALS,
            EXPONENTIATION, FUNC_BEGIN, FUNC_END, FUNC_NAME, FUNC_ARG,
            GREATER_THAN, GREATER_THAN_OR_EQUAL, INEQUALITY, LESS_THAN,
            LESS_THAN_OR_EQUAL, LOGICAL_AND, LOGICAL_OR, MULTIPLY, NUMBER,
            PARAM_NAME, POWER, SUBTRACT, TERNARY_CONDITION, TERNARY_LEFT,
            TERNARY_RIGHT, UNARY_NEG, UNARY_POS
    };

    static const char* expr_data_model_type_strs[] = 
    {
        "ADD", "BUILTIN_CONST", "BUILTIN_FUNC", "DIVIDE", "EQUALITY", "EQUALS",
            "EXPONENTIATION", "FUNC_BEGIN", "FUNC_END", "FUNC_NAME",
            "FUNC_ARG", "GREATER_THAN", "GREATER_THAN_OR_EQUAL", "INEQUALITY",
            "LESS_THAN", "LESS_THAN_OR_EQUAL", "LOGICAL_AND", "LOGICAL_OR",
            "MULTIPLY", "NUMBER", "PARAM_NAME", "POWER", "SUBTRACT",
            "TERNARY_CONDITION", "TERNARY_LEFT", "TERNARY_RIGHT", "UNARY_NEG",
            "UNARY_POS"
    };

    struct expr_object 
    {
        std::vector<expr_data_model_type> candidate_types;
        std::string value;
    };

    inline std::ostream& operator<< (std::ostream& os, const expr_object eo) 
    {
        std::cout << "{" << eo.value << ", [";

        for(int i = 0; i < eo.candidate_types.size()-1; i++)
            std::cout << expr_data_model_type_strs[eo.candidate_types[i]] << ", ";

        std::cout <<expr_data_model_type_strs[eo.candidate_types[eo.candidate_types.size()-1]];

        std::cout << "]} ";
        return os;
    }

    template <typename ELEMENT_TYPE > struct vector_of : public std::vector<ELEMENT_TYPE>
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
            void operator () (N & eo, S & v, E const& types) const
            {
                eo.value = v;

                for(int i = 0; i < types.size(); i++)
                    eo.candidate_types.push_back((expr_data_model_type)types[i]);
            }
    };

    const boost::phoenix::function<symbol_adder_impl> symbol_adder =
    boost::phoenix::function<symbol_adder_impl>(symbol_adder_impl());

    typedef std::string::const_iterator iterator_type;

}


#endif
