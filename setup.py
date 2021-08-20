from setuptools import setup, Extension

setup(  name = 'xdm',
        version = '2.3',
        description = 'Xyce(TM) XDM Netlist Translator',
        author = 'National Technology & Engineering Solutions of Sandia, LLC',
        ext_modules = [
            Extension('XdmRapidXmlReader',
                include_dirs = ['src/c_boost/xml/rapidxml'],
                libraries = ['boost_python3-mt'],
                sources = ['src/c_boost/xml/xdm_rapid.cpp']),
            Extension('SpiritExprCommon',
                libraries = ['boost_python3-mt'],
                sources = ['src/c_boost/expr/expr_parser_interface.cpp',
                    'src/c_boost/expr/hspice_expr_parser_interface.cpp',
                    'src/c_boost/expr/spectre_expr_parser_interface.cpp']),
            Extension('SpiritCommon',
                libraries = ['boost_python3-mt'],
                sources = ['src/c_boost/xyce/parser_interface.cpp',
                    'src/c_boost/xyce/xyce_parser_interface.cpp',
                    'src/c_boost/xyce/hspice_parser_interface.cpp',
                    'src/c_boost/xyce/spectre_parser_interface.cpp',
                    'src/c_boost/xyce/pspice_parser_interface.cpp',
                    'src/c_boost/xyce/tspice_parser_interface.cpp'])
                ],
        packages=['xdm'],
        package_dir={'': 'src/python'},
        package_data={'': ['*.xml']},
        scripts=['src/python/XDM'],
        )