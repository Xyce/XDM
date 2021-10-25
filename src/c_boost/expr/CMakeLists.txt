add_library(SpiritExprCommon SHARED
    expr_parser_interface.cpp
    hspice_expr_parser_interface.cpp
    spectre_expr_parser_interface.cpp
    )
target_include_directories(SpiritExprCommon
    PUBLIC ${Boost_INCLUDE_DIRS} ${Python3_INCLUDE_DIRS}
    )
target_link_libraries(SpiritExprCommon
    PUBLIC ${Boost_LIBRARIES} ${Python3_LIBRARIES}
    )
set_python_lib(SpiritExprCommon)
install_python_library(SpiritExprCommon)
