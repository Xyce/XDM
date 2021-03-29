#
# CMakeLists.txt for XDM Python files.
#
# Author: Aaron Gibson (asgibso@sandia.gov)
#

file( GLOB_RECURSE PYTHON_FILELIST
    "${CMAKE_CURRENT_SOURCE_DIR}/*"
    )
copy_files_to_build_dir( CopyPythonFiles "${CMAKE_CURRENT_SOURCE_DIR}" "${PYTHON_FILELIST}" )
