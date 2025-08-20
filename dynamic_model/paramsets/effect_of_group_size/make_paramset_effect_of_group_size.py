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

group_sizes = [25, 50, 100]

DIR_TO_STORE_PARAMSETS = (
    r"./dynamic_model/paramsets/effect_of_group_size/store_paramsets/"
)
make_dir(DIR_TO_STORE_PARAMSETS)
simulation_parameters["ARENA_WIDTH"] = 5
simulation_parameters["ARENA_HEIGHT"] = 7

for group_size in group_sizes:
    simulation_parameters["NUM_BATS"] = group_size
    simulation_parameters["OUTPUT_DIR_FOR_SIMULATION"] = (
        f"/DATA_effect_of_group_size/{group_size}/"
    )
    simulation_parameters["VARYING_PARAM"] = "NUM_BATS"

    simulation_parameters.to_csv(
        DIR_TO_STORE_PARAMSETS + f"paramset_w_group_size_{group_size}.csv"
    )
