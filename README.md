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


# Xyce(TM) XDM Netlist Translator

XDM uses CMake, the Boost Spirit header files, the Boost Python libraries, and
Python 3 to create a mixed language Python/C++ tool called xdm_bdl that can
translate PSpice, HSpice, and Spectre netlist files into Xyce-compatible
netlist files. XDM is available in binary form for Unix, Mac, and Windows
systems as part the Xyce release here [Xyce and XDM](https://xyce.sandia.gov/)
along with the XDM User's Guide. Source code for XDM and Xyce can be found here
[XDM and Xyce Source Code](https://github.com/Xyce).

There are two ways to run xdm_bdl both are available with the released version
of XDM:

    2. As a standalone executable built from xdm_bdl.py and the aforementioned
       binaries using PyInstaller. Both are available in the release of XDM

    1. As a python script xdm_bdl.py that loads the compiled XDM libraries
       SpiritCommon, SpiritExprCommon, and XdmRapidXmlReader. These are C++
       libraries that can be imported as Python 3 modules.


# Building XDM

Building XDM and it's dependents can be tricky since there are many versions of
Boost, Python 3, and C++ compilers available not all of which are compatible
with each other. In particular older versions of Boost (before Boost 1.70.0)
don't have CMake support and XDM developers may have trouble building
pre-1.70.0 Boost against later versions of Python 3 and recent C++ compilers.
XDM is developed with Boost 1.70.0 and later, Python 3.8 and 3.9, Clang 12, and
GCC 8.3 XDM's only C++11 restriction is having a C++11 compatible compiler. As
such, older compilers may work but aren't supported. Experience has shown that
more modern compilers can yield noticeable speed improvements which may be a
factor when converting large files.


# CMake configure

The XDM build should be simple given a system where the Boost Python libraries
are installed with CMake support and built against Python 3. Something like the
CMake command below should work from an empty directory intended to be the
XDM build directory.


## Configure with Boost with CMake Support

```
    cmake <path to XDM source> \
        -DBOOST_ROOT=<top level boost intallation location> \
        -DPYINSTALLER_PATH=<path to pyinstaller>
```

    
## Configure with Boost without CMake Support

In some cases the Boost CMake configuration files may not be helpful in
building XDM. In particular Windows builds of Boost seem to be missing
information required to copy the Boost Python libraries to the XDM build
directory. (This is required for the Boost-Pytnon modules on Windows). In those
cases it helps to tell CMake to not use the Boost CMake configuration files and
instead explicitly specify the Boost headers and Boost Python libraries.
    
```
    cmake <path to XDM source> \
        -DBoost_NO_BOOST_CMAKE=ON \
        -DBoost_INCLUDE_DIR=<path to boost include directory> \
        -DBoost_PYTHON38_LIBRARY_RELEASE=<path to boost-python release dir> \
        -DBoost_PYTHON38_LIBRARY_DEBUG=<path to boost-python release dir> \
        -DPYINSTALLER_PATH=<path to pyinstaller>
```

In the above either the Debug or Release version of the libraries are required
depending on which CMAKE_BUILD_TYPE is choosen. Of course the "38" in the above
snippet refers to the Python 3 major and minor version numbers used to build
the Boost Python libraries.


# Notes:

    1. CMake can be invoked from the command line on Unix-like systems with the
       command ```cmake``` or ```ccmake``` to use an interactive NCurses GUI.
       On Windows CMake also has a GUI and it works much like the Unix based
       NCurses interface.
    2. PyInstaller is optional for building XDM. If is available to CMake it
       will be used to create a standalone executable xdm_bdl that can be
       relocated and shared with others on compatible systems. If PyInstaller
       is not available then xdm_bdl.py can be used in conjunction with
       SpiritCommon, SpiritExprCommon, and XdmRapidXmlReader libraries built by
       XDM and CMake.
    3. It is generally a good idea to build CMake projects in a directory other
       than the directory that contains the source code. If 'xdm' is the XDM
       source directory in the snippet below, a good practice is to make the
       build directory a peer to the source directory:
        ```
        <path to working directory>/
            xdm/
            xdm-build/
        ```
    4. BOOST_ROOT can be set as an environment variable instead of as a CMake
       argument. The latter takes precedence if both are used.
    5. To specify which C++ compiler CMake should use see:
        - [CMake CXX](https://cmake.org/cmake/help/latest/envvar/CXX.html?highlight=cmake_cxx_compiler)
        - [CMAKE_CXX_COMPILER](https://cmake.org/cmake/help/latest/variable/CMAKE_LANG_COMPILER.html#variable:CMAKE_%3CLANG%3E_COMPILER)
    7. For available CMake build configurations see: [CMake Build Variants](https://cmake.org/cmake/help/latest/variable/CMAKE_BUILD_TYPE.html)
    8. XDM will not work with Python 2.
    9. Adding the CMake flag "-DPython3_FIND_VIRTUALENV=ONLY" helps CMake find
       the correct version of Python 3 if you are using a Python virtual
       environment. By default CMake finds the latest version of Python whether
       there is a Python interpreter in your path or not.

       
# Common CMake XDM problems:

    1. The most common XDM build problem is when Boost is built with a
       different version of Python from what CMake found in the configuration
       process. This will likely cause run-time errors and crashes with
       uninformative messages.
    2. Another problem may be that PyInstaller is not compatible with the
       Python used to build Boost. Which is a variation of the first problem.

    
# Dependencies

## Primary XDM Depenencies

    - [CMake](https://cmake.org/)
    - [Python](https://www.python.org/)
    - [Boost](https://www.boost.org/)

## CMake and finding dependencies

    - [CMake and Boost](https://cmake.org/cmake/help/latest/module/FindBoost.html#hints)
    - [CMake and Python](https://cmake.org/cmake/help/latest/module/FindPython3.html#hints)
    - Since PyInstaller is single file, there's no explicit CMake support and
       it is up to the user to specify the full path to PyInstaller as shown

       
## Package managers

    -  [SPACK](https://spack.io/) Linux, Mac
    -  [Macports](https://www.macports.org/) Mac
    -  [Homebrew](https://brew.sh/) Mac
    -  [Fink](http://www.finkproject.org/) Mac


## Installing dependencies

Boost and Python dependencies can be installed on most unix systems via the
system package manager. There are several options for local installation.
Package managers are helpful since they attempt to manage dependencies between
things like Python 3 and the Boost Python libraries. The package managers below
have been sucessfully used to build XDM dependencies. Linux package managers
work as well.

    -  [SPACK](https://spack.io/) Linux, Mac
    -  [Macports](https://www.macports.org/) Mac
    -  [Homebrew](https://brew.sh/) Mac
    -  Linux packages managers

XDM can be built on Windows 10 using the MSVC Compiler suite. We typically
install the Python binaries and build boost with MSVC. XDM has not been tested
with [Cygwin](https://www.cygwin.com/).

    -  [Python](https://www.python.org/)
    -  [Boost](https://www.boost.org/)
    -  [MSVC](https://visualstudio.microsoft.com/)


### PyInstaller

If PyInstaller isn't available with the systems's Python installation or is
outdated a Python virtual environment can be used to install a local version of
PyInstaller that is compatible with the system's Python 3 installation.

    - To create a Python virtual environment and activate it
      ```
      python3 -m venv venv
      source ./venv/bin/activate
      ```
    - Install pip and then PyInstaller. The proxy settings may not be necessary

      ```
      export HTTPS_PROXY=<proxy address>
      pip install PyInstaller
      ```
    - Test PyInstaller before building XDM

      ```
      echo "print('Hello')" > hello.py
      PyInstaller hello.py
      ./dist/hello/hello
      ```
    - PyInstaller may also be available via a system compatible package manager
    - For more details see [Python Virtual Environemnts](https://docs.python.org/3/tutorial/venv.html)
