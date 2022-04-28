# Xyce(TM) XDM Netlist Translator
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
along with this program.  If not, see <http://www.gnu.org/licenses/>.


# XDM 2.5.0 Release Notes

## General

- Translations of netlists using binned models will no longer have the
\texttt{.OPTION PARSER MODEL\_BINNING=TRUE} statement. This option is
turned on by default in \Xyce{} now and therefore no longer needs to be 
explicitly declared.

- Duplicate output variables will now be removed from the \texttt{.PRINT} 
line.

- The expression and function pre-processing capabilities have been 
removed from XDM.

## spectre
      
- The \texttt{else} conditional block in \texttt{if-else} statments will 
now be commented out by XDM, since conditional statement support is not 
fully mature yet in \Xyce{}.

## PSpice

- Fixed bug where instance parameters for temperature coefficients for 
resistors were not translated.
