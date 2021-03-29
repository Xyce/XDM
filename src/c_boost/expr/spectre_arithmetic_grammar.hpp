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


#ifndef SPECTRE_ARITHMETIC_GRAMMAR_H
#define SPECTRE_ARITHMETIC_GRAMMAR_H

#include "ast_common.hpp"
#include <boost/spirit/include/qi.hpp>


namespace {
namespace qi = boost::spirit::qi;
namespace ascii = boost::spirit::ascii;
}

template <typename Iterator>
struct SpectreArithmeticGrammar : boost::spirit::qi::grammar<Iterator,
    ast_common::root(), boost::spirit::ascii::space_type>
{

    qi::rule<Iterator, ast_common::expr(), ascii::space_type> expression, term, power;

    qi::rule<Iterator, ast_common::boolExpr(), ascii::space_type> logical, relational;

    qi::rule<Iterator, ast_common::operand(), ascii::space_type> factor;

    qi::rule<Iterator, ast_common::number(), ascii::space_type> constant;

    qi::rule<Iterator, ast_common::variable(), ascii::space_type> variable;

    qi::rule<Iterator, ast_common::assignment(), ascii::space_type> assignment;

    qi::rule<Iterator, ast_common::funcAssignment(), ascii::space_type> func_assignment;

    qi::rule<Iterator, ast_common::funcEval(), ascii::space_type> function;

    qi::rule<Iterator, ast_common::builtIn(), ascii::space_type> built_in;

    qi::rule<Iterator, ast_common::ternary(), ascii::space_type> ternary_rule;

    qi::rule<Iterator, ast_common::root(), ascii::space_type> start;

    qi::rule<Iterator, std::string(), ascii::space_type> any, eq, gt, gtoe,
        func_begin, func_identifier, func_end, func_separator, identifier,
        ineq, logical_and, logical_or, lt, ltoe, math_expression, numeric,
        number, parenthetical_math_expression, raw_first_identifier,
        raw_identifier, m_e, m_log2e, m_log10e, m_ln2, m_ln10, m_pi, m_two_pi,
        m_pi_2, m_pi_4, m_1_pi, m_2_pi, m_2_sqrtpi, m_sqrt2, m_sqrt1_2,
        m_degperrad, p_q, p_c, p_k, p_h, p_eps0, p_u0, p_celsius0,
        natural_logarithm, logarithm10, exponent, cosine, sine, tangent,
        agauss, built_in_constant_identifier, built_in_function,
        built_in_function_identifier, square_root, aunif, arccosine, arcsine,
        arctangent, maximum, minimum, integer, absolute_value, signum,
        absolute_power, signed_power, hyperbolic_cosine, hyperbolic_sine,
        hyperbolic_tangent, ternary_condition, ternary_expression, add,
        subtract, multiply, divide, power_double_asterisk, power_caret;

    qi::rule<Iterator> white_space;

    SpectreArithmeticGrammar() : SpectreArithmeticGrammar::base_type(start)
    {
        using qi::char_;
        using qi::hold;
        using qi::lit;
        using ascii::no_case;


        identifier = 
            raw_first_identifier >> *(raw_identifier | numeric)
            ;

        raw_first_identifier = 
            ~char_("0-9$?:;(){}[],.= \t'*/+<>&|!-")
            ;

        raw_identifier = 
            +(~char_("$?:;(){}[],= \t'*/+<>&|!-"))
            ;

        white_space = 
            +char_(" \t")
            ;

        any = 
            *(char_)
            ;

        numeric = 
            +char_("0-9")
            ;

        logical_or = 
            char_("|") >> char_("|")
            ;

        logical_and = 
            char_("&") >> char_("&")
            ;

        ineq = 
            char_("!") >> char_("=")
            ;

        eq = 
            char_("=") >> char_("=")
            ;

        gtoe = 
            char_(">") >> char_("=")
            ;

        ltoe = 
            char_("<") >> char_("=")
            ;

        gt = 
            char_(">")
            ;

        lt = 
            char_("<")
            ;

        add = 
            char_("+")
            ;

        subtract =
            char_("-")
            ;

        multiply =
            char_("*")
            ;

        divide =
            char_("/")
            ;

        power_double_asterisk = 
            char_("*") >> char_("*")
            ;

        power_caret = 
            char_("^")
            ;

        number = 
            hold[numeric >> -(char_(".") >> -numeric) >> no_case[char_("e") >> -(char_("-") | char_("+")) >> numeric]] | 
            hold[numeric >> -(char_(".") >> -numeric) >> no_case[char_("fHsV")]] |
            hold[numeric >> -(char_(".") >> -numeric) >> no_case[char_("PTGMKafpnumck")]] >> no_case[char_("fHsV")] |
            hold[numeric >> -(char_(".") >> -numeric) >> no_case[char_("PTGMKafpnumck")]] |
            hold[numeric >> -(char_(".") >> -numeric)] |
            hold[char_(".") >> numeric >> no_case[char_("e") >> -(char_("-") | char_("+")) >> numeric]] | 
            hold[char_(".") >> numeric >> no_case[char_("fHsV")]] |
            hold[char_(".") >> numeric >> char_("PTGMKkcmunpfa")] >> no_case[char_("fHsV")] |
            hold[char_(".") >> numeric >> char_("PTGMKkcmunpfa")] |
            hold[char_(".") >> numeric]
            ;

        parenthetical_math_expression = 
            char_("(") >> +(hold[parenthetical_math_expression] | hold[+char_("a-zA-Z0-9,.+/*_<>!= \t|$&?:~-")]) >> char_(")")
            ;

        math_expression =
            +(hold[parenthetical_math_expression >> -(+char_("a-zA-Z0-9.+/*_<>!= \t|$&?:~-"))] | hold[+char_("a-zA-Z0-9.+/*_<>!= \t|$&~?:-") >> -parenthetical_math_expression])
            ;

        ternary_condition =
            +(hold[parenthetical_math_expression >> -(+char_("a-zA-Z0-9.+/*_<>!= \t|$&~-"))] | hold[+char_("a-zA-Z0-9.+/*_<>!= \t|$&~-") >> -parenthetical_math_expression])
            ;

        ternary_expression =
            +(hold[parenthetical_math_expression >> -(-char_("-") >> +char_("a-zA-Z0-9._! \t|$&~"))] | hold[-char_("-") >> +char_("a-zA-Z0-9._! \t|$&~") >> -parenthetical_math_expression])
            ;

        func_begin = 
            char_("(")
            ;

        func_end = 
            char_(")")
            ;

        func_separator = 
            char_(",")
            ;

        func_identifier = 
            identifier >> -white_space >> func_begin >> hold[math_expression] >> *(func_separator >> hold[math_expression]) >> func_end
            ;

        m_e =
            hold[char_("M") >> char_("_") >> char_("E")]
            ;

        m_log2e =
            hold[char_("M") >> char_("_") >> char_("L") >> char_("O") >> char_("G") >> char_("2") >> char_("E")]
            ;

        m_log10e =
            hold[char_("M") >> char_("_") >> char_("L") >> char_("O") >> char_("G") >> char_("1") >> char_("0") >> char_("E")]
            ;

        m_ln2 =
            hold[char_("M") >> char_("_") >> char_("L") >> char_("N") >> char_("2")]
            ;

        m_ln10 =
            hold[char_("M") >> char_("_") >> char_("L") >> char_("N") >> char_("1") >> char_("0")]
            ;

        m_pi =
            hold[char_("M") >> char_("_") >> char_("P") >> char_("I")]
            ;

        m_pi_2 =
            hold[char_("M") >> char_("_") >> char_("P") >> char_("I") >> char_("_") >> char_("2")]
            ;

        m_pi_4 =
            hold[char_("M") >> char_("_") >> char_("P") >> char_("I") >> char_("_") >> char_("4")]
            ;

        exponent =
            hold[no_case[char_("e")] >> no_case[char_("x")] >> no_case[char_("p")]]
            ;

        natural_logarithm =
            hold[no_case[char_("l")] >> no_case[char_("o")] >> no_case[char_("g")]]
            ;

        logarithm10 =
            hold[no_case[char_("l")] >> no_case[char_("o")] >> no_case[char_("g")] >> char_("1") >> char_("0")]
            ;

        cosine =
            hold[no_case[char_("c")] >> no_case[char_("o")] >> no_case[char_("s")]]
            ;

        sine =
            hold[no_case[char_("s")] >> no_case[char_("i")] >> no_case[char_("n")]]
            ;

        tangent =
            hold[no_case[char_("t")] >> no_case[char_("a")] >> no_case[char_("n")]]
            ;

        arccosine =
            hold[no_case[char_("a")] >> no_case[char_("c")] >> no_case[char_("o")] >> no_case[char_("s")]]
            ;

        arcsine =
            hold[no_case[char_("a")] >> no_case[char_("s")] >> no_case[char_("i")] >> no_case[char_("n")]]
            ;

        arctangent =
            hold[no_case[char_("a")] >> no_case[char_("t")] >> no_case[char_("a")] >> no_case[char_("n")]]
            ;

        hyperbolic_cosine =
            hold[no_case[char_("c")] >> no_case[char_("o")] >> no_case[char_("s")] >> no_case[char_("h")]]
            ;

        hyperbolic_sine =
            hold[no_case[char_("s")] >> no_case[char_("i")] >> no_case[char_("n")] >> no_case[char_("h")]]
            ;

        hyperbolic_tangent =
            hold[no_case[char_("t")] >> no_case[char_("a")] >> no_case[char_("n")] >> no_case[char_("h")]]
            ;

        square_root =
            hold[no_case[char_("s")] >> no_case[char_("q")] >> no_case[char_("r")] >> no_case[char_("t")]]
            ;

        agauss =
            hold[no_case[char_("a")] >> no_case[char_("g")] >> no_case[char_("a")] >> no_case[char_("u")] >> 
            no_case[char_("s")] >> no_case[char_("s")]]
            ;

        aunif =
            hold[no_case[char_("a")] >> no_case[char_("u")] >> no_case[char_("n")] >> no_case[char_("i")] >> 
            no_case[char_("f")]]
            ;

        maximum =
            hold[no_case[char_("m")] >> no_case[char_("a")] >> no_case[char_("x")]]
            ;

        minimum =
            hold[no_case[char_("m")] >> no_case[char_("i")] >> no_case[char_("n")]]
            ;

        integer =
            hold[no_case[char_("i")] >> no_case[char_("n")] >> no_case[char_("t")]]
            ;

        absolute_value =
            hold[no_case[char_("a")] >> no_case[char_("b")] >> no_case[char_("s")]]
            ;

        signum =
            hold[no_case[char_("s")] >> no_case[char_("g")] >> no_case[char_("n")]]
            ;

        absolute_power =
            hold[no_case[char_("p")] >> no_case[char_("o")] >> no_case[char_("w")]]
            ;

        signed_power =
            hold[no_case[char_("p")] >> no_case[char_("w")] >> no_case[char_("r")]]
            ;

        built_in_constant_identifier =
            m_e | m_log2e | m_log10e | m_ln2 | m_ln10 | m_pi_2 | m_pi_4 | m_pi
            ;

        built_in_function_identifier =
            exponent | logarithm10 | natural_logarithm | cosine | sine | tangent | arccosine | arcsine | arctangent | square_root | agauss | aunif |
            maximum | minimum | integer | absolute_value | signum | absolute_power | signed_power | hyperbolic_cosine | hyperbolic_sine | hyperbolic_tangent
            ;

        built_in_function = 
            built_in_function_identifier >> func_begin >> hold[math_expression] >> *(func_separator >> hold[math_expression]) >> func_end
            ;

        built_in =
            hold[built_in_constant_identifier] | hold[built_in_function]
            ;

        start =
            hold[assignment] | hold[func_assignment] | hold[logical] | hold['\'' >> logical >> '\'']
            ;

        assignment =
            hold[identifier >> char_('=') >> !char_('=') >> logical] |
            hold[identifier >> char_('=') >> '\'' >> logical >> '\'']
            ;

        func_assignment =
            hold[func_identifier >> char_('=') >> any] |
            hold[func_identifier >> char_('=') >> '\'' >> any >> '\'']
            ;

        logical =
            relational >> *(hold[(logical_or >> relational)] |
                            hold[(logical_and >> relational)])
            ;

        relational =
            expression >> *(hold[(ineq  >> expression)] |
                            hold[(eq >> expression)] |
                            hold[(gtoe >> expression)] |
                            hold[(ltoe >> expression)] |
                            hold[(gt >> expression)] |
                            hold[(lt >> expression)])
            ;

        expression =
            term >> *(hold[(char_('+') >> term)] | hold[(char_('-') >> term)])
            ;

        term =
            power >> *(hold[(char_('*') >> power)] | hold[(char_('/') >> power)])
            ;

        power =
            factor >> *(hold[(power_double_asterisk >> factor)] | hold[(power_caret >> factor)])
            ;

        factor =
            hold[ternary_rule] | hold[constant] | hold[built_in] | hold[function] | hold[variable] | '(' >> logical >> ')' |
            (char_('-') >> factor) | (char_('+') >> factor)
            ;

        constant =
            number
            ;

        variable =
            identifier
            ;

        function =
            func_identifier
            ;

        ternary_rule =
            ternary_condition >> char_('?') >> ternary_condition >> char_(':') >> ternary_expression
            ;
    };
};

#endif
