#!/bin/sh

# Parse outputs from GPUMD trajectory outputs (tdep_fit_configurations.xyz)
tdep_parse_output --temperature 50 tdep_fit_configurations.xyz

# Don't proceed until parsing completes
wait

# Extract force constants using 4 porcessors with 11 angstrom cutoff from 2nd and 6 angstrom cutoff from 3rd force consnts
mpirun -np 4 extract_forceconstants --temperature 50 -rc2 11 -rc3 6 > extract_fcs.log

# Don't proceed unit fitting is completed
wait

# Rename outputs to input for kALDo
mv outfile.forceconstant infile.forceconstant
mv outfile.forceconstant_thirdorder infile.forceconstant_thirdorder
