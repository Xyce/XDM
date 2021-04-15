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
along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Building XDM

XDM uses CMake to build a standalone Python executable ```xdm_bdl```.
```xdm_bdl``` has dependencies on Python 3, ```pyinstaller```, and the
Boost-python library. The Python installation used to build XDM should be the
same Python installation used to build the Boost-python libraries. When
building XDM, CMake attempts to find Boost and Python by looking in standard
installation locations as well as environment variables ```PATH``` and
```BOOST_ROOT```. As this doesn't always work, more details follow.


## Out of source build with CMake

It is generally a good idea to build binaries in a directory other than the
directory that contains the source code. A good practice is to make the build
directory a peer to the source directory:

  ```
  <path to working directory>/
      data-model/
      data-model-build
  ```

In the above ```data-model``` is the source code for XDM and
```data-model-build``` is the build directory. Some developers choose to use
a subdirectory of their source tree for building as in ```<path to working
directory>/data-model/build```. Either way is fine.


## Configure: Invoking CMake

New CMake users may want to run CMake interactively via the Windows CMake GUI
or on Linux/Mac via the CMake ncurses interface. These tools prompt the user to
specify locations for Boost and Python dependencies if the paths found by CMake
are incorrect. This process can be iterated until the depdencies are
satisfied.

The Windows CMake GUI has entry boxes to specify the source and build
directories. The NCurses interface accepts the source directory as its first
argument and should be invoked from the buidl directory.

The same dependencies set interactively can be specified when invoking
```ccmake```, Windows GUI or NCurses interface, and also ```cmake```,
non-interactive command line tool. For example, to build XDM with Clang and
Python 3.8:

```
cmake $HOME/xdm-stack/data-model/data-model \
  -DBoost_NO_BOOST_CMAKE=ON \
  -DBoost_PYTHON_VERSION:STRING=python3.8 \
  -DCMAKE_BUILD_TYPE:STRING=Release \
  -DCMAKE_CXX_COMPILER:FILEPATH=`which clang++` \
  -DCMAKE_C_COMPILER:FILEPATH=`which clang` \
```

The above depends on the env var BOOST_ROOT being set to the boost-python
installation and having ```python``` and ```pyinstaller``` in the PATH
environemnt variable.


## Python

If CMake doesn't find the Python libraries, it may be helpful to change the
last line to ```-DBoost_PYTHON_VERSION:STRING=python3```, though specifying
only the major version may not be portable across platforms.

If the above command fails in finding Python and its components, ```python```
and ```pyinstaller``` can be fully specified by adding the lines:

```
  -DPYINSTALLER_PATH:FILEPATH=<path to pyinstaller> \
  -DPYTHON_INCLUDE_DIR:PATH=<dir path to pyconfig.h> \
  -DPYTHON_LIBRARY:FILEPATH=<path to libpython3.8.{ext}> \
```

The paths for PYTHON_INCLUDE_DIR and PYTHON_LIBRARY can be found using the
```python--config``` command or possibly ```python3-config``` with the
arguments ```--includes``` and ```--prefix```. PYTHON_INCLUDE_DIR should not
include "-I" and PYTHON_LIBRARY should be the full path to the library. The
libray name can be found via ```python-config --libs```.


## Boost

CMake has two ways to find Boost. First is to search for Boost headers and
libraries relative to the value of the environment variable ```BOOST_ROOT```.
Ths second is to use CMake config files created by the Boost intallation
process.


To use the first method set the env var ```BOOST_ROOT``` to point to the root
of the Boost Python installetion and add the following lines to the CMake
configuration::

```
-DBoost_NO_BOOST_CMAKE=ON \
-DBoost_PYTHON_VERSION:STRING=python3.8 \
```

Typically you might encounter Boost Python libraries named like this
```libboost_<Boost_PYTHON_VERSION><X>.<ext>``` where ```Boost_PYTHON_VERSION```
may be ```python3.8, python38, python3, or python```. To account for this
```Boost_PYTHON_VERSION``` defaults to ```python3``` but should be set by the
user as above if CMake fails to find Boost.

The second is to use CMake config files ```BoostConfig.cmake``` or
```boost_python-config.camke```. To tell CMake to use the isntalled Boost
Config files add the following lines to the CMake configuration:

```
-DBoost_NO_BOOST_CMAKE=OFF \
-DBoost_DIR=<dir path to BoostConfig.cmake or boost_python-config.cmake> \
-DBoost_PYTHON_VERSION:STRING=python3.8 \
```

Again, the value of ```Boost_PYTHON_VERSION``` may vary with platform and Boost
installation.

See (Boost CMake)[https://cmake.org/cmake/help/latest/module/FindBoost.html]
for more details.


## Compiler

CMake uses the environment variables ```CXX``` and ```CC``` to find a usable
C++ and C compiler. Failing that, CMake searches the ```PATH``` env var for
gcc, g++, and for other popular compiler names. If CMake finds the wrong
compiler then the use can force CMake to use a specific compiler by setting the
above variables or by pasing the the arguments

```
-DCMAKE_C_COMPILER:PATH=<path to c compiler> \
-DCMAKE_CXX_COMPILER:PATH=<path to cxx compiler> \
```

## Building 

After a successful CMake configuration, XDM can be built from the build
directory using ```make package```, or the cmake command

```cmake --build . --config Release --target package```

The target ```package``` invokes pyinstaller to create the standalone
exectuable ```xdm_bdl```. Upon a successful build ```xdm_bdl``` can be found at
```<build-dir>/xdm_bundle/dist/xdm_bdl``` and in the newly create zip or tar
file. This compressed file can be extracted on a different but compatible
system and the ```xdm_bdl``` executable can be run there.


## Debugging CMake configuration problems

A good way to debug an errant CMake configuration or build is to check the
above variables (in <build-dir>/CMakeCache.txt) and rerun CMake with the
correct paths to these depenencies. Removing CMakeCache.txt and all ./C*
subdirectories from the build directory may help CMake use your new settings.
Starting from an empty build directory is often a good solution.


## Installing dependencies

Boost and Python dependencies can be installed on most unix systems via the
system package manager. There are several options for local installation

    *  [SPACK](https://spack.io/) Linux, Mac
    *  [Macports](https://www.macports.org/) Mac
    *  [Homebrew](https://brew.sh/) Mac
    *  [Fink](http://www.finkproject.org/) Mac

XDM can be built on Windows 10 using the MSVC Compiler suite. We typically
install the Python binaries and build boost with MSVC. XDM has not been tested
with [Cygwin](https://www.cygwin.com/).

    *  [Python](https://www.python.org/)
    *  [Boost](https://www.boost.org/)
    *  [MSVC](https://visualstudio.microsoft.com/)


### PyInstaller

On many systems, the Python installation may be outdated or can't be changed by
the user. In that case a Python virtual environment is helpul. This allows any
user to install pyinstaller and provides a consistent way to build XDM across
platforms and machines. On Linux and Mac if Python3 is available the steps are:

* create a Python virtual environment and activate it

```
python3 -m venv venv
source ./venv/bin/activate
```

* Install pip and then pyinstaller. The proxy settings may not be necessary

```
export HTTPS_PROXY=<proxy address>
pip install pyinstaller
```

* Test pyinstaller before building XDM

```
echo "print('Hello')" > hello.py
pyinstaller hello.py
./dist/hello/hello
```

For more details see (Python Virtual Environemnts)[https://docs.python.org/3/tutorial/venv.html]


### Boost

Boost can be built with the Python3 virtual enviroment active. Detailed
instructions to build Boost can be found at the link above, see "Getting
Started". Note that when building boost-python with the Python virtual
environment it may be necessary to specify the Python include paths obtained
from ```python-config --includes``` in your ```project-config.jam``` or
```user-config.jam```. The line specifying Python looks similar too:

```
    using python : 3.8 : "<path to python virtual env" : <path to pyconfig.h> ;
```

Note the use of ':' and ':'.

Although Boost added Python3 support for version 1.58.0 earlier version of
Boost may be incompatible with later versions of Python and vice-versa. XDM
2.1.0 was tested with Python 3.8 and Boost 1.73.0.
