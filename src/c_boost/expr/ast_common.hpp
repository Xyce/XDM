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


#ifndef AST_COMMON_HPP
#define AST_COMMON_HPP

#include <boost/spirit/include/qi.hpp>
#include <boost/variant/recursive_variant.hpp>
#include <boost/variant/apply_visitor.hpp>
#include <boost/fusion/include/adapt_struct.hpp>
#include <boost/foreach.hpp>
#include <boost/algorithm/string.hpp>

// Get M_PI from Boost for MSVC since it requires math.c in MSV
#if _MSC_VER && !__INTEL_COMPILER
#include <boost/math/constants/constants.hpp>
const double M_PI = boost::math::constants::pi<double>();
#endif

#include <algorithm>
#include <cmath> 
#include <limits>
#include <map>
#include <random>
#include <string>
#include <unordered_map>
#include <sstream>

#include "boost_expr_parser_common.h"


namespace ast_common
{
    struct nil {};
    struct unary;
    struct expr;
    struct boolExpr;
    struct assignment;
    struct funcAssignment;
    struct funcEval;
    struct builtIn;
    struct ternary;
    struct variable;
    struct root;
    struct number;

    typedef boost::variant< nil, boost::recursive_wrapper<unary>, boost::recursive_wrapper<boolExpr>, boost::recursive_wrapper<expr>, boost::recursive_wrapper<assignment>,
        boost::recursive_wrapper<funcAssignment>, boost::recursive_wrapper<funcEval>, boost::recursive_wrapper<root>, boost::recursive_wrapper<variable>, 
        boost::recursive_wrapper<number>, boost::recursive_wrapper<builtIn>, boost::recursive_wrapper<ternary> > operand;

    struct unary
    {
        char sign;
        operand operand_;
    };

    struct operation
    {
        std::string op;
        operand operand_;
    };

    struct expr 
    {
        operand first;
        std::list<operation> rest;
    };

    struct boolOperation
    {
        std::string op;
        operand operand_;
    };

    struct boolExpr 
    {
        operand first;
        std::list<boolOperation> rest;
    };

    struct assignment
    {
        std::string name;
        char op;
        operand rhs;
    };

    struct funcAssignment
    {
        std::string func_name;
        char op;
        std::string func_expr;
    };

    struct funcEval
    {
        std::string func_name;
    };

    struct builtIn
    {
        std::string func_name;
    };

    struct ternary
    {
        std::string conditional;
        char op1;
        std::string left;
        char op2;
        std::string right;
    };

    struct root
    {
        operand first;
    };

    struct variable
    {
        std::string var_name;
    };

    struct number
    {
        std::string constant_number;
    };

    template <typename Grammar>
    struct evaluator;

    template <typename Grammar>
    struct printer
    {
        printer(std::unordered_map<std::string, double> & variable_map, std::unordered_map<std::string, std::map<int, std::string>> & function_variable_map, std::unordered_map<std::string, std::string> & function_map, const Grammar & g, std::vector<expr_boost_common::expr_object> & expr_parse_results)
            : variable_map(variable_map), function_variable_map(function_variable_map), function_map(function_map), g(g), expr_parse_results(expr_parse_results) { }

        typedef void result_type;
        std::unordered_map<std::string, double> & variable_map;
        std::unordered_map<std::string, std::map<int, std::string>> & function_variable_map;
        std::unordered_map<std::string, std::string> & function_map;
        const Grammar & g;
        std::vector<expr_boost_common::expr_object> & expr_parse_results;

        void operator()(nil) {}

        void operator()(variable const& x) 
        {
            expr_boost_common::expr_object obj;
            obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::PARAM_NAME);
            obj.value = x.var_name;
            expr_parse_results.push_back(obj);
        }

        void operator()(number const& x) 
        {
            expr_boost_common::expr_object obj;
            obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::NUMBER);
            obj.value = x.constant_number;
            expr_parse_results.push_back(obj);
        }

        void operator()(operation const& x) 
        {
            boost::apply_visitor(*this, x.operand_);

            expr_boost_common::expr_object obj;
            obj.value = x.op;

            if(x.op == "+")
            {
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::ADD);
            }
            else if(x.op == "-")
            {
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::SUBTRACT);
            }
            else if(x.op == "*")
            {
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::MULTIPLY);
            }
            else if(x.op == "/")
            {
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::DIVIDE);
            }
            else if(x.op == "**" || x.op == "^")
            {
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::POWER);
            }

            expr_parse_results.push_back(obj);
        }

        void operator()(boolOperation const& x) 
        {
            boost::apply_visitor(*this, x.operand_);

            expr_boost_common::expr_object obj;
            obj.value = x.op;
            if(x.op == "||")
            {
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::LOGICAL_OR);
            }
            else if(x.op == "&&")
            {
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::LOGICAL_AND);
            }
            else if(x.op == "!=")
            {
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::INEQUALITY);
            }
            else if(x.op == "==")
            {
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::EQUALITY);
            }
            else if(x.op == ">=")
            {
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::GREATER_THAN_OR_EQUAL);
            }
            else if(x.op == "<=")
            {
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::LESS_THAN_OR_EQUAL);
            }
            else if(x.op == ">")
            {
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::GREATER_THAN);
            }
            else if(x.op == "<")
            {
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::LESS_THAN);
            }

            expr_parse_results.push_back(obj);
        }

        void operator()(unary const& x) 
        {
            boost::apply_visitor(*this, x.operand_);

            expr_boost_common::expr_object obj;
            obj.value = x.sign;
            switch (x.sign)
            {
                case '-':
                    obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::UNARY_NEG);
                    break;
                case '+':
                    obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::UNARY_POS);
                    break;
            }

            expr_parse_results.push_back(obj);
        }

        void operator()(expr const& x) 
        {
            boost::apply_visitor(*this, x.first);
            BOOST_FOREACH(operation const& oper, x.rest)
            {
                (*this)(oper);
            }
        }

        void operator()(boolExpr const& x) 
        {
            boost::apply_visitor(*this, x.first);
            BOOST_FOREACH(boolOperation const& oper, x.rest)
            {
                (*this)(oper);
            }
        }

        void operator()(assignment const& x) 
        {
            boost::apply_visitor(*this, x.rhs);
        }

        void operator()(funcAssignment const& x) 
        {
        }

        void operator()(funcEval const& x) 
        {
            std::string identifier = x.func_name;
            std::vector<std::string> args;
            std::string curr_func_name;
            std::string arguments;
            std::string curr_arg;
            int arg_num = 0;
            size_t open_parenthesis_count = 0;
            size_t close_parenthesis_count = 0;
            bool embedded_func = false;

            // isolate the function name from it's arguments
            boost::trim_if(identifier, boost::is_any_of("\r\n\t "));
            size_t equals_idx = identifier.find_first_of("(");
            curr_func_name = identifier.substr(0, equals_idx);
            arguments = identifier.substr(equals_idx+1);
            arguments = arguments.substr(0, arguments.length()-1);

            expr_boost_common::expr_object obj;
            obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::FUNC_NAME);
            obj.value = curr_func_name;
            expr_parse_results.push_back(obj);
            obj.candidate_types.pop_back();
            obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::FUNC_BEGIN);
            obj.value = "(";
            expr_parse_results.push_back(obj);

            boost::split(args, arguments, boost::is_any_of(","), boost::token_compress_on);
            for(int i = 0; i < args.size(); i++)
            {
                // check if argument is actually a function with multiple inputs (which would 
                // of been split because the delimiter is ","), re-construct the function 
                // string if it is
                expr_boost_common::expr_object arg_obj;

                if(curr_arg.empty())
                {
                    curr_arg = args[i];
                    embedded_func = false;
                }
                else
                {
                    curr_arg += ",";
                    curr_arg += args[i];
                }

                open_parenthesis_count = std::count(curr_arg.begin(), curr_arg.end(), '(');
                if(open_parenthesis_count > 0)
                {
                    embedded_func = true;
                    close_parenthesis_count = std::count(curr_arg.begin(), curr_arg.end(), ')');
                    if(open_parenthesis_count != close_parenthesis_count)
                    {
                        continue;
                    }
                }
                else
                {
                    curr_arg = args[i];
                }

                arg_obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::FUNC_ARG);
                arg_obj.value = curr_arg;
                expr_parse_results.push_back(arg_obj);

                curr_arg = "";
                arg_num++;
            }

            obj.candidate_types.pop_back();
            obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::FUNC_END);
            obj.value = ")";
            expr_parse_results.push_back(obj);

        }

        void operator()(builtIn const& x) 
        {
            std::string identifier = x.func_name;
            std::vector<std::string> args;
            std::string curr_func_name;
            std::string arguments;
            std::string curr_arg;
            int arg_num = 0;
            size_t open_parenthesis_count = 0;
            size_t close_parenthesis_count = 0;
            bool embedded_func = false;

            // isolate the function name from it's arguments
            boost::trim_if(identifier, boost::is_any_of("\r\n\t "));
            size_t equals_idx = identifier.find_first_of("(");
            expr_boost_common::expr_object obj;

            if (equals_idx == std::string::npos)
            {
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::BUILTIN_CONST);
                obj.value = identifier;
                expr_parse_results.push_back(obj);
            }
            else
            {
                curr_func_name = identifier.substr(0, equals_idx);
                arguments = identifier.substr(equals_idx+1);
                arguments = arguments.substr(0, arguments.length()-1);

                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::BUILTIN_FUNC);
                obj.value = curr_func_name;
                expr_parse_results.push_back(obj);
                obj.candidate_types.pop_back();
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::FUNC_BEGIN);
                obj.value = "(";
                expr_parse_results.push_back(obj);

                boost::split(args, arguments, boost::is_any_of(","), boost::token_compress_on);
                for(int i = 0; i < args.size(); i++)
                {
                    // check if argument is actually a function with multiple inputs (which would 
                    // of been split because the delimiter is ","), re-construct the function 
                    // string if it is
                    expr_boost_common::expr_object arg_obj;

                    if(curr_arg.empty())
                    {
                        curr_arg = args[i];
                        embedded_func = false;
                    }
                    else
                    {
                        curr_arg += ",";
                        curr_arg += args[i];
                    }

                    open_parenthesis_count = std::count(curr_arg.begin(), curr_arg.end(), '(');
                    if(open_parenthesis_count > 0)
                    {
                        embedded_func = true;
                        close_parenthesis_count = std::count(curr_arg.begin(), curr_arg.end(), ')');
                        if(open_parenthesis_count != close_parenthesis_count)
                        {
                            continue;
                        }
                    }
                    else
                    {
                        curr_arg = args[i];
                    }

                    arg_obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::FUNC_ARG);
                    arg_obj.value = curr_arg;
                    expr_parse_results.push_back(arg_obj);

                    curr_arg = "";
                    arg_num++;
                }

                obj.candidate_types.pop_back();
                obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::FUNC_END);
                obj.value = ")";
                expr_parse_results.push_back(obj);

            }
        }

        void operator()(ternary const& x) 
        {
            expr_boost_common::expr_object obj;
            obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::TERNARY_CONDITION);
            obj.value = x.conditional;
            expr_parse_results.push_back(obj);

            obj.candidate_types.pop_back();
            obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::TERNARY_LEFT);
            obj.value = x.left;
            expr_parse_results.push_back(obj);

            obj.candidate_types.pop_back();
            obj.candidate_types.push_back(expr_boost_common::expr_data_model_type::TERNARY_RIGHT);
            obj.value = x.right;
            expr_parse_results.push_back(obj);
        }

        void operator()(root const& x) 
        {
            boost::apply_visitor(*this, x.first);
        }
    };

    template <typename Grammar>
    struct evaluator
    {
        evaluator(std::unordered_map<std::string, double> & variable_map, std::unordered_map<std::string, std::map<int, std::string>> & function_variable_map, std::unordered_map<std::string, std::string> & function_map, const Grammar & g)
            : variable_map(variable_map), function_variable_map(function_variable_map), function_map(function_map), g(g) { }

        typedef double result_type;
        std::unordered_map<std::string, double> & variable_map;
        std::unordered_map<std::string, std::map<int, std::string>> & function_variable_map;
        std::unordered_map<std::string, std::string> & function_map;
        const Grammar & g;

        double operator()(nil) { BOOST_ASSERT(0); return 0; }

        double operator()(variable const& x) 
        {
            if(variable_map.find(x.var_name) == variable_map.end())
            {
                return std::numeric_limits<double>::quiet_NaN();
            }
            else
            {
                return variable_map[x.var_name];
            }
        }

        double operator()(number const& x) 
        { 
            std::string value = x.constant_number;

            switch(value.back())
            {
                case 'u': case 'U':
                    value.pop_back();
                    value += "e-6";
                    break;
                case 'n': case 'N':
                    value.pop_back();
                    value += "e-9";
                    break;
                case 'p': case 'P':
                    value.pop_back();
                    value += "e-12";
                    break;
                case 'f': case 'F':
                    value.pop_back();
                    value += "e-15";
                    break;
                case 'a': case 'A':
                    value.pop_back();
                    value += "e-18";
                    break;
                case 'm': case 'M':
                    value.pop_back();
                    value += "e-3";
                    break;
                case 'k': case 'K':
                    value.pop_back();
                    value += "e3";
                    break;
                case 'x': case 'X':
                    value.pop_back();
                    value += "e6";
                    break;
                case 'g': case 'G':
                    value.pop_back();
                    value += "e9";
                    break;
            }

            std::istringstream in_value(value);
            double v;
            in_value >> v;

            return v; 
        }

        double operator()(operation const& x, double lhs)
        {
            double rhs = boost::apply_visitor(*this, x.operand_);
            if(x.op == "+")
            {
                return lhs + rhs;
            }
            else if(x.op == "-")
            {
                return lhs - rhs;
            }
            else if(x.op == "*")
            {
                return lhs * rhs;
            }
            else if(x.op == "/")
            {
                return lhs / rhs;
            }
            else if(x.op == "**" || x.op == "^")
            {
                return pow(lhs, rhs);
            }

            BOOST_ASSERT(0);
            return 0;
        }

        double operator()(boolOperation const& x, double lhs)
        {
            if(isnan(lhs))
            {
                return std::numeric_limits<double>::quiet_NaN();
            }

            double rhs = boost::apply_visitor(*this, x.operand_);

            if(isnan(rhs))
            {
                return std::numeric_limits<double>::quiet_NaN();
            }

            if(x.op == "||")
            {
                return lhs || rhs;
            }
            else if(x.op == "&&")
            {
                return lhs && rhs;
            }
            else if(x.op == "!=")
            {
                return lhs != rhs;
            }
            else if(x.op == "==")
            {
                return lhs == rhs;
            }
            else if(x.op == ">=")
            {
                return lhs >= rhs;
            }
            else if(x.op == "<=")
            {
                return lhs <= rhs;
            }
            else if(x.op == ">")
            {
                return lhs > rhs;
            }
            else if(x.op == "<")
            {
                return lhs < rhs;
            }
            BOOST_ASSERT(0);
            return 0;
        }

        double operator()(unary const& x)
        {
            double rhs = boost::apply_visitor(*this, x.operand_);
            switch (x.sign)
            {
                case '-': return -rhs;
                case '+': return +rhs;
            }
            BOOST_ASSERT(0);
            return 0;
        }

        double operator()(expr const& x) 
        {
            double state = boost::apply_visitor(*this, x.first);
            BOOST_FOREACH(operation const& oper, x.rest)
            {
                state = (*this)(oper, state);
            }
            return state;
        }

        double operator()(boolExpr const& x) 
        {
            double state = boost::apply_visitor(*this, x.first);
            BOOST_FOREACH(boolOperation const& oper, x.rest)
            {
                state = (*this)(oper, state);
            }
            return state;
        }

        double operator()(assignment const& x) 
        {
            double state = boost::apply_visitor(*this, x.rhs);

            variable_map[x.name] = state;

            return state;
        }

        double operator()(funcAssignment const& x) 
        {
            std::vector<std::string> args;
            boost::split(args, x.func_name, boost::is_any_of("(),"), boost::token_compress_on);
            function_map[args[0]] = x.func_expr;
            for(int i = 1; i < args.size()-1; i++)
            {
                function_variable_map[args[0]][i-1] = args[i];
            }

            return 0;
        }

        double operator()(funcEval const& x) 
        {
            std::string identifier = x.func_name;
            std::vector<std::string> args;
            std::unordered_map<std::string, double> global_variable_map;
            std::string curr_func_name;
            std::string arguments;
            std::string curr_arg;
            int arg_num = 0;
            size_t open_parenthesis_count = 0;
            size_t close_parenthesis_count = 0;
            typedef root ast_root;

            // isolate the function name from it's arguments
            boost::trim_if(identifier, boost::is_any_of("\r\n\t "));
            size_t equals_idx = identifier.find_first_of("(");
            curr_func_name = identifier.substr(0, equals_idx);
            arguments = identifier.substr(equals_idx+1);
            arguments = arguments.substr(0, arguments.length()-1);

            boost::split(args, arguments, boost::is_any_of(","), boost::token_compress_on);
            for(int i = 0; i < args.size(); i++)
            {
                // check if argument is actually a function with multiple inputs (which would 
                // of been split because the delimiter is ","), re-construct the function 
                // string if it is
                if(curr_arg.empty())
                {
                    curr_arg = args[i];
                }
                else
                {
                    curr_arg += ",";
                    curr_arg += args[i];
                }

                open_parenthesis_count = std::count(curr_arg.begin(), curr_arg.end(), '(');
                if(open_parenthesis_count > 0)
                {
                    close_parenthesis_count = std::count(curr_arg.begin(), curr_arg.end(), ')');
                    if(open_parenthesis_count != close_parenthesis_count)
                    {
                        continue;
                    }
                }
                else
                {
                    curr_arg = args[i];
                }

                // Evaluate each argument's value by running the phrase_parse on the argument (which is
                // stored as a string.
                evaluator<Grammar> eval(variable_map, function_variable_map, function_map, g);
                ast_root arg_top;
                boost::spirit::ascii::space_type space;

                phrase_parse_routine(curr_arg, g, space, arg_top);

                // Set the value of each argument for the scope of the function. These may be different
                // from a variable's global value. For example, globally there may be a variable defined
                // as "x=7". A function declaration may also use the same variable name, i.e. "f(x)=x+1".
                // The variable "x" may be set to a different number in the scope of the function, but 
                // this should not affect the global definition
                double eval_result = eval(arg_top);
                global_variable_map [function_variable_map[curr_func_name][arg_num]] = variable_map[function_variable_map[curr_func_name][arg_num]];
                variable_map[function_variable_map[curr_func_name][arg_num]] = eval_result;

                // check if any of the arguments are NaN. If so, restore variable map and return NaN as result
                if(isnan(eval_result))
                {
                    for(auto const & elem:global_variable_map)
                    {
                        variable_map[elem.first] = elem.second;
                    }

                    return std::numeric_limits<double>::quiet_NaN();
                }

                curr_arg = "";
                arg_num++;
            }

            // Evaluate function's value by running the phrase_parse on the function string
            evaluator<Grammar> eval(variable_map, function_variable_map, function_map, g);
            ast_root top;
            boost::spirit::ascii::space_type space;

            phrase_parse_routine(function_map[curr_func_name], g, space, top);

            double v = eval(top);

            for(auto const & elem:global_variable_map)
            {
                variable_map[elem.first] = elem.second;
            }

            return v;
        }

        double operator()(builtIn const& x) 
        {
            std::string identifier = x.func_name;
            std::vector<std::string> args;
            std::vector<double> built_in_function_arguments;
            std::string curr_func_name;
            typedef root ast_root;

            // isolate the function name from it's arguments
            boost::trim_if(identifier, boost::is_any_of("\r\n\t "));

            if(identifier.find("(") != std::string::npos)
            {
                size_t equals_idx = identifier.find_first_of("(");
                std::string curr_arg;
                std::string arguments;
                size_t open_parenthesis_count = 0;
                size_t close_parenthesis_count = 0;
                curr_func_name = identifier.substr(0, equals_idx);
                arguments = identifier.substr(equals_idx+1);
                arguments = arguments.substr(0, arguments.length()-1);

                boost::split(args, arguments, boost::is_any_of(","), boost::token_compress_on);
                for(int i = 0; i < args.size(); i++)
                {
                    // check if argument is actually a function with multiple inputs (which would 
                    // of been split because the delimiter is ","), re-construct the function 
                    // string if it is
                    if(curr_arg.empty())
                    {
                        curr_arg = args[i];
                    }
                    else
                    {
                        curr_arg += ",";
                        curr_arg += args[i];
                    }

                    open_parenthesis_count = std::count(curr_arg.begin(), curr_arg.end(), '(');
                    if(open_parenthesis_count > 0)
                    {
                        close_parenthesis_count = std::count(curr_arg.begin(), curr_arg.end(), ')');
                        if(open_parenthesis_count != close_parenthesis_count)
                        {
                            continue;
                        }
                    }
                    else
                    {
                        curr_arg = args[i];
                    }

                    // Evaluate each argument's value by running the phrase_parse on the argument (which is
                    // stored as a string.
                    evaluator<Grammar> eval(variable_map, function_variable_map, function_map, g);
                    ast_root arg_top;
                    boost::spirit::ascii::space_type space;

                    phrase_parse_routine(curr_arg, g, space, arg_top);

                    double eval_result = eval(arg_top);

                    // check if any of the arguments are NaN. If so, return NaN as result
                    if(isnan(eval_result))
                    {
                        return std::numeric_limits<double>::quiet_NaN();
                    }

                    built_in_function_arguments.push_back(eval_result);

                    curr_arg = "";
                }
            }
            else
            {
                curr_func_name = identifier;
            }

            if(boost::iequals("pi", curr_func_name))
            {
                return M_PI;
            }
            else if(boost::iequals("exp", curr_func_name))
            {
                return exp(built_in_function_arguments[0]);
            }
            else if(boost::iequals("log", curr_func_name))
            {
                return log(built_in_function_arguments[0]);
            }
            else if(boost::iequals("log10", curr_func_name))
            {
                return log10(built_in_function_arguments[0]);
            }
            else if(boost::iequals("cos", curr_func_name))
            {
                return cos(built_in_function_arguments[0]);
            }
            else if(boost::iequals("sin", curr_func_name))
            {
                return sin(built_in_function_arguments[0]);
            }
            else if(boost::iequals("tan", curr_func_name))
            {
                return tan(built_in_function_arguments[0]);
            }
            else if(boost::iequals("acos", curr_func_name))
            {
                return acos(built_in_function_arguments[0]);
            }
            else if(boost::iequals("asin", curr_func_name))
            {
                return asin(built_in_function_arguments[0]);
            }
            else if(boost::iequals("atan", curr_func_name))
            {
                return atan(built_in_function_arguments[0]);
            }
            else if(boost::iequals("cosh", curr_func_name))
            {
                return cosh(built_in_function_arguments[0]);
            }
            else if(boost::iequals("sinh", curr_func_name))
            {
                return sinh(built_in_function_arguments[0]);
            }
            else if(boost::iequals("tanh", curr_func_name))
            {
                return tanh(built_in_function_arguments[0]);
            }
            else if(boost::iequals("sqrt", curr_func_name))
            {
                return sqrt(built_in_function_arguments[0]);
            }
            else if(boost::iequals("agauss", curr_func_name))
            {
                double nominal = built_in_function_arguments[0];
                double variation;

                if(built_in_function_arguments.size() == 2)
                {
                    variation = built_in_function_arguments[1];
                }
                else
                {
                    variation = built_in_function_arguments[1]/built_in_function_arguments[2];
                }

                std::default_random_engine generator;
                std::normal_distribution<double> distribution(nominal, variation);

                return 0*distribution(generator);
            }
            else if(boost::iequals("aunif", curr_func_name))
            {
                double nominal = built_in_function_arguments[0];
                double variation;

                if(built_in_function_arguments.size() == 2)
                {
                    variation = built_in_function_arguments[1];
                }
                else
                {
                    variation = built_in_function_arguments[1]/built_in_function_arguments[2];
                }

                std::default_random_engine generator;
                std::uniform_real_distribution<double> distribution(-variation, variation);

                return 0*(distribution(generator)+nominal);
            }
            else if(boost::iequals("max", curr_func_name))
            {
                return std::max(built_in_function_arguments[0], built_in_function_arguments[1]);
            }
            else if(boost::iequals("min", curr_func_name))
            {
                return std::min(built_in_function_arguments[0], built_in_function_arguments[1]);
            }
            else if(boost::iequals("int", curr_func_name))
            {
                return int(built_in_function_arguments[0]);
            }
            else if(boost::iequals("abs", curr_func_name))
            {
                return std::abs(built_in_function_arguments[0]);
            }
            else if(boost::iequals("sgn", curr_func_name))
            {
                if(built_in_function_arguments[0] < 0)
                    return -1;
                else if(built_in_function_arguments[0] > 0)
                    return 1;
                else
                    return 0;
            }
            else if(boost::iequals("pow", curr_func_name))
            {
                return pow(built_in_function_arguments[0], int(built_in_function_arguments[1]));
            }
            else if(boost::iequals("pwr", curr_func_name))
            {
                if(built_in_function_arguments[0] < 0)
                    return -1*pow(std::abs(built_in_function_arguments[0]), built_in_function_arguments[1]);
                else 
                    return pow(std::abs(built_in_function_arguments[0]), built_in_function_arguments[1]);
            }

            BOOST_ASSERT(0);
            return 0;
        }

        double operator()(ternary const& x)
        {
            typedef root ast_root;

            evaluator<Grammar> eval(variable_map, function_variable_map, function_map, g);
            ast_root top;
            boost::spirit::ascii::space_type space;

            phrase_parse_routine(x.conditional, g, space, top);

            double conditional = eval(top);

            // check if conditional is NaN. if so, discontinue and return NaN
            if(isnan(conditional))
            {
                return std::numeric_limits<double>::quiet_NaN();
            }

            if(conditional == 0)
            {
                phrase_parse_routine(x.right, g, space, top);

                return eval(top);
            }
            else 
            {
                phrase_parse_routine(x.left, g, space, top);

                return eval(top);
            }
            BOOST_ASSERT(0);
            return 0;
        }

        double operator()(root const& x) 
        {
            double state = boost::apply_visitor(*this, x.first);

            return state;
        }
    };


    template <typename Grammar, typename Skipper, typename ... Args>
    void phrase_parse_routine(const std::string& input, const Grammar& g, const Skipper& s, Args&& ... args)
    {
        std::string::const_iterator start = input.begin();
        std::string::const_iterator end = input.end();

        bool r = phrase_parse(start, end, g, s, std::forward<Args>(args) ...);

        if(!(r && start == end))
        {
            // std::cout << "Error parsing: " << input << std::endl;
            // std::cout << "Unparseable: " << std::string(start, end) << std::endl;
            // throw std::runtime_error("Parse error");
        }
    }


    template <typename Grammar>
    void process_input(const std::string& input, const Grammar& g, std::unordered_map<std::string, double> & variable_map, std::unordered_map<std::string, std::map<int, std::string>> & function_variable_map, std::unordered_map<std::string, std::string> & function_map, double & out_val)
    {
        try 
        {
            typedef root ast_root;
            evaluator<Grammar> eval(variable_map, function_variable_map, function_map, g);
            ast_root top;
            boost::spirit::ascii::space_type space;

            phrase_parse_routine(input, g, space, top);

            out_val = eval(top);
        }
        catch (std::exception& e) 
        {
            // std::cout << "EXCEPTION: " << e.what() << std::endl;
        }

        return;
    }
}

BOOST_FUSION_ADAPT_STRUCT(
    ast_common::variable,
    (std::string, var_name)
)

BOOST_FUSION_ADAPT_STRUCT(
    ast_common::number,
    (std::string, constant_number)
)

BOOST_FUSION_ADAPT_STRUCT(
    ast_common::unary,
    (char, sign)
    (ast_common::operand, operand_)
)

BOOST_FUSION_ADAPT_STRUCT(
    ast_common::operation,
    (std::string, op)
    (ast_common::operand, operand_)
)

BOOST_FUSION_ADAPT_STRUCT(
    ast_common::expr,
    (ast_common::operand, first)
    (std::list<ast_common::operation>, rest)
)

BOOST_FUSION_ADAPT_STRUCT(
    ast_common::boolOperation,
    (std::string, op)
    (ast_common::operand, operand_)
)

BOOST_FUSION_ADAPT_STRUCT(
    ast_common::boolExpr,
    (ast_common::operand, first)
    (std::list<ast_common::boolOperation>, rest)
)

BOOST_FUSION_ADAPT_STRUCT(
    ast_common::assignment,
    (std::string, name)
    (char, op)
    (ast_common::operand, rhs)
)

BOOST_FUSION_ADAPT_STRUCT(
    ast_common::funcAssignment,
    (std::string, func_name)
    (char, op)
    (std::string, func_expr)
)

BOOST_FUSION_ADAPT_STRUCT(
    ast_common::funcEval,
    (std::string, func_name)
)

BOOST_FUSION_ADAPT_STRUCT(
    ast_common::builtIn,
    (std::string, func_name)
)

BOOST_FUSION_ADAPT_STRUCT(
    ast_common::ternary,
    (std::string, conditional)
    (char, op1)
    (std::string, left)
    (char, op2)
    (std::string, right)
)

BOOST_FUSION_ADAPT_STRUCT(
    ast_common::root,
    (ast_common::operand, first)
)

#endif
