add_library(SpiritExprCommon SHARED
    expr_parser_interface.cpp
    hspice_expr_parser_interface.cpp
    spectre_expr_parser_interface.cpp
    )
target_link_libraries(SpiritExprCommon ${PYTHON_LIBRARY} ${Boost_LIBRARIES})
set_python_lib(SpiritExprCommon)
install_python_library(SpiritExprCommon)
