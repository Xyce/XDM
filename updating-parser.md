Steps for adding new devices
 - Add grammar rules to src/c_boost/xyce/SpectreGrammar.hpp (usually by copying/tweaking rules from XyceParser)
	- write/copy rule for device_dev_type
	- write rule for device
		- Remember to add rule for optional parenthesis
	- add to device = (resistor | inductor ...) rule
	- add to initial iterators

 - In src/python/xdm/inout/readers/XDMFactory.py
	- update model_map_dict

 - In src/python/xdm/inout/readers/SpectreNetlistBoostParserInterface.py
	- update spectre_to_adm_model_type_map

 - `make install` in src/c_boost/build 
 - Add device definition to src/python/spectre_5_0.xml

 To test
 - In src/python/test/unit/inout/readers 

	python -m unittest Test_Spectre_Boost_Reader

 - Honestly didn't write very many in here. Testing was largely done by using [this bash script](https://gitlab.sandia.gov/xdm/data-model/blob/master/src/python/convert.sh) which calls xdm.py and inspecting output files