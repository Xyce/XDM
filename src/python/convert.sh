
CONVERTER_SCRIPT="./xdm.py"

# INPUT_FILENAME="spectre-capacitor.cir"
# INPUT_FILE="./test/unit/resources/${INPUT_FILENAME}"
# INPUT_FILE="./test/unit/resources/c7passives-test.scs"
INPUT_FILE="./test/unit/resources/spectre-unit-test.sp"
INPUT_XML="./test/unit/resources/spectre.xml"
INPUT_FILE_FORMAT="spectre"
OUTPUT_XML="./test/unit/resources/xyce.xml"
OUTPUT_FILE_FORMAT="xyce"
OUTPUT_DIR="./out/"


echo "Converting..."

python $CONVERTER_SCRIPT $INPUT_FILE $INPUT_FILE_FORMAT $OUTPUT_DIR $OUTPUT_FILE_FORMAT

echo "Converted file located in $OUTPUT_DIR"

