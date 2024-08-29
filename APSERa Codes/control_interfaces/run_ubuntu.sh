#!/bin/bash

# Start the APlusLauncher.exe
wine Aplus/APlusLauncher.exe

# Add a delay of 10 seconds
sleep 10
python Cryotel_controller_1.2.py &
python lakeshore_controller.py &
python lakeshore_editcurve.py &
python powersupply_controller.py
