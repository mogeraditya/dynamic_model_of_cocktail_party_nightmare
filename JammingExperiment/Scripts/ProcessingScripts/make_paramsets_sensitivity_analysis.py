import json
import sys
from itertools import product

import numpy as np

sys.path.append("./dynamic_model")

from supporting_files.utilities import load_parameters, make_dir

simulation_parameters = load_parameters(
    r"./JammingExperiment/Data/InputData/common_parameters.json"
)
dir_to_store = r"./JammingExperiment/Data/InputData/sensitivity_params/"
make_dir(dir_to_store)


call_durations = [0.002, 0.005]
call_rates_fast = [10, 20]
# emitted_spls = [80, 100]
hearing_thresholds = [40, 60, 80]
bat_speeds = [1, 3, 5]
call_directionalities = [7, 10]
# hearing_directionalities = [2, 7]
# bat_rotation_speed = [, 540] # pcik 360
forward_masking_curve = ["full", "chopped"]
time_delay_for_direction_change = [0.006, 0.012, 0.024]
bat_radial_resolution = [0.002, 0.004]
# bat_angular_resolution = [15, 30, 60]
memory_window_for_consistency = [3, 5, 10]
bat_frontal_range = [30, 60, 90]

# spatial_reference_frame = ["allocentric", "egocentric"]
# jammer_resolutions = [1, 100]

# number_of_consistent_ipis_for_movement = np.ceil(
#     np.array(memory_window_for_consistency) / 2
# )
# time_delay_for_repulsion = time_delay_for_direction_change

array_of_param_values = [
    # call_durations,
    # call_rates_fast,
    # # emitted_spls,
    # hearing_thresholds,
    bat_speeds,
    # call_directionalities,
    # # hearing_directionalities,
    # # bat_rotation_speed,
    # forward_masking_curve,
    # time_delay_for_direction_change,
    # bat_radial_resolution,
    # # bat_angular_resolution,
    # memory_window_for_consistency,
    # bat_frontal_range,
    # # spatial_reference_frame,
    # # jammer_resolutions,
]
array_of_param_labels = [
    # "CALL_DURATION",
    # "CALL_RATE_FAST",
    # # "EMITTED_SPL",
    # "HEARING_THRESHOLD",
    "BAT_SPEED",
    # "CALL_DIRECTIONALITY",
    # # "HEARING_DIRECTIONALITY",
    # # "BAT_ROTATION_SPEED",
    # "TEMPORAL_MASKING_FN_TYPE",
    # "TIME_DELAY_FOR_DIRECTION_CHANGE",
    # "BAT_RADIAL_RESOLUTION",
    # # "BAT_ANGULAR_RESOLUTION",
    # "MEMORY_WINDOW_FOR_CONSISTENCY",
    # "BAT_FRONTAL_RANGE",
    # # "SPATIAL_REFERENCE_FRAME",
    # # "JAMMER_RESOLUTION",
]

list_of_combinations = list(product(*array_of_param_values))
print(len(list(product(*array_of_param_values))))

output_dir_counter = 0

# error_files = [
#     3767,
#     2518,
#     2977,
#     2028,
#     3704,
#     2494,
#     2769,
#     2478,
#     2034,
#     3707,
#     3153,
#     3041,
#     2440,
#     2163,
#     622,
#     289,
#     1312,
#     876,
#     1926,
#     5505,
#     5693,
#     5686,
#     4981,
#     4924,
#     3876,
#     5560,
#     4361,
#     3858,
#     5666,
#     4814,
#     4263,
#     4384,
#     4475,
#     6462,
#     5753,
#     7366,
#     7622,
#     6391,
#     7009,
#     7773,
#     6159,
#     7282,
#     7320,
#     7403,
#     1742,
#     1089,
#     4273,
#     249,
#     4967,
#     3225,
# ]
error_files = [4758]
for item in list_of_combinations:
    # if output_dir_counter in error_files:
    simulation_parameters["OUTPUT_DIR_FOR_SIMULATION"] = (
        f"/sensitivity_analysis/paramset_{output_dir_counter}/"
    )
    for i, param_label in enumerate(array_of_param_labels):
        simulation_parameters[param_label] = item[i]

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
