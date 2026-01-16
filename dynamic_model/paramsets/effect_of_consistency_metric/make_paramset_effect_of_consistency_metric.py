import csv
import math
import os
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.append("./dynamic_model")

from supporting_files.utilities import load_parameters, make_dir

simulation_parameters = load_parameters(
    r"./dynamic_model/paramsets/common_parameters.csv"
)

# We will vary num_bats and generate multiple paramsets for different number of bats keeping everything else the same.

consistent_frames = [1, 2, 3, 4, 5]

DIR_TO_STORE_PARAMSETS = (
    r"./dynamic_model/paramsets/effect_of_consistency_metric/store_paramsets/"
)
make_dir(DIR_TO_STORE_PARAMSETS)
# simulation_parameters["ARENA_WIDTH"] = 7
# simulation_parameters["ARENA_LENGTH"] = 5
# simulation_parameters["NUM_BATS"] = 25
# simulation_parameters["SIM_DURATION"] = 10
for count in consistent_frames:
    simulation_parameters["NUMBER_OF_CONSISTENT_IPIS_FOR_MOVEMENT"] = count
    simulation_parameters["OUTPUT_DIR_FOR_SIMULATION"] = (
        f"/NVG_effect_of_consistency_metric/{count}_out_of_5/"
    )
    simulation_parameters["VARYING_PARAM"] = "TIME_DELAY_FOR_DIR_CHANGE"

    simulation_parameters.to_csv(
        DIR_TO_STORE_PARAMSETS + f"paramset_w_consistency_{count}_out_of_5.csv"
    )
