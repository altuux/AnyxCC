#!/bin/sh
# Anyx CC - Launch Script

# Directory
DIR="$(dirname "$0")"
cd "$DIR"

# Python libs
export PYSDL2_DLL_PATH="/usr/trimui/lib"
export LD_LIBRARY_PATH="/usr/trimui/lib:$LD_LIBRARY_PATH"

# launch
python3 main.py

# cleanup
unset LD_LIBRARY_PATH