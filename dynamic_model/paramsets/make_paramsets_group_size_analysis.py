import json
import sys
from itertools import product

import numpy as np
import pandas as pd

sys.path.append("./dynamic_model")

from supporting_files.utilities import load_parameters, make_dir

simulation_parameters = load_parameters(r"./dynamic_model/paramsets/test_group.json")
dir_to_store = r"./dynamic_model/paramsets/effect_of_group_size/"
make_dir(dir_to_store)


group_sizes = [5, 10, 30, 50, 75, 100]

df_arena_size = pd.read_csv("./dynamic_model/paramsets/arena_sizes_with_group_size.csv")

array_of_param_values = group_sizes
param_label = "NUM_BATS"

# list_of_combinations = list(product(*array_of_param_values))
# print(len(list(product(*array_of_param_values))))

output_dir_counter = 0

for i, group_size in enumerate(group_sizes):
    # if output_dir_counter in error_files:
    simulation_parameters["OUTPUT_DIR_FOR_SIMULATION"] = (
        f"/effect_of_group_size/paramset_{output_dir_counter}/"
    )

    simulation_parameters[param_label] = group_size
    simulation_parameters["ARENA_LENGTH"] = df_arena_size["arena length"][i]
    simulation_parameters["ARENA_WIDTH"] = df_arena_size["arena width"][i]

    simulation_parameters["NUMBER_OF_CONSISTENT_IPIS_FOR_MOVEMENT"] = np.ceil(
        simulation_parameters["MEMORY_WINDOW_FOR_CONSISTENCY"] / 2
    )
    simulation_parameters["TIME_DELAY_THRESHOLD_FOR_REPULSION"] = simulation_parameters[
        "TIME_DELAY_FOR_DIRECTION_CHANGE"
    ]
    simulation_parameters["BAT_FAST_SPEED"] = simulation_parameters["BAT_SPEED"]
    simulation_parameters["PARAM_LABEL"] = f"paramset_{output_dir_counter}"

    with open(
        dir_to_store + f"/paramset_number_{output_dir_counter}.json",
        "w",
        encoding="utf-8",
    ) as fp:
        json.dump(simulation_parameters, fp)

    output_dir_counter += 1
