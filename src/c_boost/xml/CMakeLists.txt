#
# CMakeLists.txt for xml
#

include_directories( rapidxml )

set( XDM_RAPID_SRC
    xdm_rapid.cpp
    )
add_library( XdmRapidXmlReader SHARED ${XDM_RAPID_SRC} )
target_link_libraries ( XdmRapidXmlReader ${PYTHON_LIBRARY} ${Boost_LIBRARIES} )
set_python_lib( XdmRapidXmlReader )
install_python_library( XdmRapidXmlReader )
