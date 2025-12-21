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

group_sizes = [5, 10, 30]
call_rates = [10]
behaviour_rules = ["consistency", "loudest_sound"]

DIR_TO_STORE_PARAMSETS = (
    r"./dynamic_model/paramsets/effect_of_lot_of_shit/store_paramsets/"
)
make_dir(DIR_TO_STORE_PARAMSETS)
simulation_parameters["ARENA_WIDTH"] = 7
simulation_parameters["ARENA_HEIGHT"] = 7
simulation_parameters["SIM_DURATION"] = 15
simulation_parameters["TIME_DELAY_THRESHOLD_FOR_REPULSION"] = 0.008

for group_size in group_sizes:
    for call_rate in call_rates:
        for behaviour_rule in behaviour_rules:
            if behaviour_rule == "loudest_sound":
                simulation_parameters["TIME_DELAY_THRESHOLD_FOR_REPULSION"] = 0.03
                simulation_parameters["TIME_DELAY_FOR_DIRECTION_CHANGE"] = 0.03
            else:
                simulation_parameters["TIME_DELAY_THRESHOLD_FOR_REPULSION"] = 0.008
                simulation_parameters["TIME_DELAY_FOR_DIRECTION_CHANGE"] = 0.008

            simulation_parameters["BEHAVIOUR_RULE"] = behaviour_rule
            simulation_parameters["NUM_BATS"] = group_size
            simulation_parameters["CALL_RATE"] = call_rate
            simulation_parameters["OUTPUT_DIR_FOR_SIMULATION"] = (
                f"/DATA_effect_of_lot_of_shit/group_size_{group_size}_call_rate_{call_rate}_rule_{behaviour_rule}/"
            )
            # simulation_parameters["VARYING_PARAM"] = ["NUM_BATS", "CALL_RATE"]
            simulation_parameters["VARYING_PARAM_1"] = "NUM_BATS"
            simulation_parameters["VARYING_PARAM_2"] = "CALL_RATE"
            simulation_parameters["VARYING_PARAM_3"] = "BEHAVIOUR_RULE"

            simulation_parameters.to_csv(
                DIR_TO_STORE_PARAMSETS
                + f"paramset_w_group_size_{group_size}_call_rate_{call_rate}_rule_{behaviour_rule}.csv"
            )
