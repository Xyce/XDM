#
# CMakeLists.txt for XDM Python files.
#
# Author: Aaron Gibson (asgibso@sandia.gov)
#

file( GLOB_RECURSE PYTHON_FILELIST
    "${CMAKE_CURRENT_SOURCE_DIR}/*"
    )
# Remove xdm.py.in from the above
list(REMOVE_ITEM PYTHON_FILELIST xdm.py.in)
copy_files_to_build_dir( CopyPythonFiles "${CMAKE_CURRENT_SOURCE_DIR}" "${PYTHON_FILELIST}" )
