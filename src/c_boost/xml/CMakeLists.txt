add_library(XdmRapidXmlReader SHARED 
    xdm_rapid.cpp
    )
target_include_directories(XdmRapidXmlReader
    PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/rapidxml/rapidxml-1.13
    ${Boost_INCLUDE_DIRS} ${Python3_INCLUDE_DIRS}
    )
target_link_libraries(XdmRapidXmlReader
    PUBLIC ${Boost_LIBRARIES} ${Python3_LIBRARIES}
    )
set_python_lib( XdmRapidXmlReader )
install_python_library( XdmRapidXmlReader )
