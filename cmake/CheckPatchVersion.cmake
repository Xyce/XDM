#
# CheckPatchVersion.cmake 
# 
# Author: Aaron Gibson (asgibso@sandia.gov)
#
# This script is executed to determine if the XDM_PATCH_VERSION needs
# to be reloaded.
#
# This script expects the following variables to be defined in order
# to execute correctly:
# - CMAKE_COMMAND
# - PROJECT_SOURCE_DIR
# - PROJECT_BINARY_DIR
# - GIT_EXECUTABLE
# - PATCH_VERSION_FILE
#
# Note also that this script is expected to be run from a directory
# where git can find its repository.
#
execute_process( COMMAND ${CMAKE_COMMAND} -E touch "${GIT_HASH_FILE}" )
execute_process(
	COMMAND ${GIT_EXECUTABLE} rev-parse --short --verify HEAD
	WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
	OUTPUT_VARIABLE GIT_HASH_CHECK_RAW
)
string( STRIP "${GIT_HASH_CHECK_RAW}" GIT_HASH_VAR )

file( READ ${GIT_HASH_FILE} ORIG_VERSION_STR )

if( NOT "${ORIG_VERSION_STR}" STREQUAL "${GIT_HASH_VAR}" )
	file( WRITE ${GIT_HASH_FILE} ${GIT_HASH_VAR} )
	# Instruct CMake to re-run
	execute_process(
		WORKING_DIRECTORY "${PROJECT_BINARY_DIR}"
		COMMAND ${CMAKE_COMMAND} "${PROJECT_SOURCE_DIR}"
	)
endif()

