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

time_delays = [0.01, 0.02, 0.05, 0.07]

DIR_TO_STORE_PARAMSETS = (
    r"./dynamic_model/paramsets/effect_time_delay_of_decision/store_paramsets/"
)
make_dir(DIR_TO_STORE_PARAMSETS)
simulation_parameters["ARENA_WIDTH"] = 5
simulation_parameters["ARENA_HEIGHT"] = 7
simulation_parameters["NUM_BATS"] = 20
for time_delay in time_delays:
    simulation_parameters["TIME_DELAY_FOR_DIR_CHANGE"] = time_delay
    simulation_parameters["OUTPUT_DIR_FOR_SIMULATION"] = (
        f"/DATA_effect_time_delay_of_decision/{time_delay}/"
    )
    simulation_parameters["VARYING_PARAM"] = "TIME_DELAY_FOR_DIR_CHANGE"

    simulation_parameters.to_csv(
        DIR_TO_STORE_PARAMSETS + f"paramset_w_time_delay_{time_delay}.csv"
    )
