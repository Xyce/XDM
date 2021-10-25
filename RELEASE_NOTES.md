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
along with this program.  If not, see <http://www.gnu.org/licenses/>.


# XDM 2.4.0 Release Notes

## General

    - Fixed bug where relative path names to files in .lib statements were
      incorrect.
    - Substitutions done by XDM for the special variable TEMP are no longer
      necessary and are taken out in this release.

      
## PSpice

    - XDM allows the undocumented PSpice syntax of having trailing commas in
      entries of "TABLE" statements.

      
## HSPICE

    - if/else/endif statements in HSPICE are now commented out since
        Xyce doesn't currently support this.
    - Node names containing brackets, as seen in HSPICE, are now
        allowed.
    - Forward slashes in HSPICE device and subckt names are now allowed.
    - Xyce’s “-hspice-ext” option, which should be used when running HSPICE
        netlists translated by XDM, now by default expects the “.” for the
        subcircuit hierarchy separator character. Therefore, XDM translations
        will leave that character unchanged rather than translating it to
        Xyce’s native “:” subcircuit separator character.
    - Secondary sweep of .DC analyses should now be translated correctly
        into Xyce.
    - Xyce can now handle resistors with solution dependent expressions for
        their resistance values. Therefore, XDM will no longer translate
        solution dependent resistors into behavioral B-element sources.


## spectre

    - XDM now translates transient Spectre "sine" specifications.
    - XDM comments out Spectre dc analysis statements with no parameters as it
      is not clear what the Xyce equivalent should be.
    - XDM can now identify Spectre device instantiations of models defined in
      SPICE format.
    - XDM removes Spectre "trise" parameter for R and C devices since this
      isn't available in Xyce.
    - Fixed bug in Spectre translation where sometimes the model name would not
      appear for a instantiation of a device of that model.
    - Fixed XDM crash when processing some Spectre subcircuit definitions.
    - Fixed bug in translation of Spectre “include” statements that have the
      parameter “section”. These will now be translated into “.LIB” statements
      in Xyce.
    - Added support for translation of Spectre “port” device instantiations.
      Not all instance parameters are translated at this time.
    - Translate the "M" unit prefix (mega) in Spectre "AC" statements to
      the Xyce equivalent "X".
    - XDM comments out Spectre dc analysis statements with no
        parameters as it is not clear what the Xyce equivalent should be.
    - Fixed bug where XDM aborted when translating Spectre “include”
        files with paths containing hyphens.
