from setuptools import setup, Extension
import setuptools.command.build_py
import os

XDM_VERSION = "2.4.0"

class config_build(setuptools.command.build_py.build_py):
    def run(self):
        source_file = os.path.join(os.path.dirname(__file__),
                "src", "python", "xdm.py.in")
        with open(source_file, 'r') as fi:
            src_data = fi.read()
        target_file = os.path.join(os.path.dirname(__file__),
                "src", "python", "xdm_bdl.py")
        with open(target_file, 'w') as fo:
            fo.write(src_data.replace(
                "@XDM_MAJOR_VERSION@.@XDM_MINOR_VERSION@.@XDM_PATCH_VERSION@",
                XDM_VERSION))
        setuptools.command.build_py.build_py.run(self)

setup(  name = 'xdm_bdl',
        version = XDM_VERSION,
        description = 'Xyce(TM) XDM Netlist Translator',
        author = 'National Technology & Engineering Solutions of Sandia, LLC',
        ext_modules = [
            Extension('XdmRapidXmlReader',
                include_dirs = ['src/c_boost/xml/rapidxml/rapidxml-1.13'],
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
        package_dir={'': 'src/python'},
        packages=['xdm'],
        package_data={'': ['*.xml']},
        scripts=['src/python/xdm_bdl.py'],
        cmdclass={'build_py': config_build,},
        )
