add_library(SpiritCommon SHARED
    hspice_parser_interface.cpp
    parser_interface.cpp
    pspice_parser_interface.cpp
    spectre_parser_interface.cpp
    tspice_parser_interface.cpp
    xyce_parser_interface.cpp
    )
target_include_directories(SpiritCommon
    PUBLIC ${Boost_INCLUDE_DIRS} ${Python3_INCLUDE_DIRS}
    )
target_link_libraries(SpiritCommon
    PUBLIC ${Boost_LIBRARIES} ${Python3_LIBRARIES}
    )
set_python_lib(SpiritCommon)
install_python_library(SpiritCommon)
