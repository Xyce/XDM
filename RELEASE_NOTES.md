# Xyce(TM) XDM Netlist Translator
Xyce(TM) XDM Netlist Translator
Copyright 2002-2020 National Technology & Engineering Solutions of
Sandia, LLC (NTESS).  Under the terms of Contract DE-NA0003525 with
NTESS, the U.S. Government retains certain rights in this software.
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/.

# XDM 2.6.0 Release Notes

## General

\item XDM now allows models to be redefined within the same scope
        without raising an exception. Previously, the code would exit out
        if a model was redefined. Now, it will just emit a warning.
        
## HSpice

\item HSPICE expressions can be delimited by double quotes. XDM would
    either let this pass through without making any changes (which
    would cause problems with the resultant Xyce netlist), or comment
    it out in some cases (mostly, in expressions in sources). This was
    fixed by adding a HSPICE grammar rule that defines expressions
    delimited by double quotes, and then adding code in the parser
    interface to change the expression delimiters to curly braces.
    
## SPECTRE

\item XDM now tranlates the SPECTRE model parameter "VERSION" to "version".
