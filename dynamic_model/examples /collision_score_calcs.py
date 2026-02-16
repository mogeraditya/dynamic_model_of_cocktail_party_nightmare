import glob
import pickle
import sys

import matplotlib.pyplot as plt
import scipy as scp

sys.path.append("./dynamic_model/")
import numpy as np
from scores.collision_scores import (
    compute_collision_counts_and_length,
    compute_collision_rate,
)
from scores.run_all_score_calculations import filter_bat_positions_from_history
from supporting_files.utilities import load_history_dump, load_parameters

history_output_dir = "./MISC/testing_groups/10_bats_test_small_size_null/"

list_of_dict_files = glob.glob(history_output_dir + "/history_dump_*.pkl")
list_of_dict_files = np.sort(list_of_dict_files)

list_containing_data_from_all_pickle_files = []
for pickle_file in list_of_dict_files:
    with open(pickle_file, "rb") as f:
        _list_containing_subset = pickle.load(f)
        list_containing_data_from_all_pickle_files.extend(_list_containing_subset)

parameter_file = glob.glob(history_output_dir + "/parameters_used.json")[0]
parameter_df = load_parameters(parameter_file)

with open(history_output_dir + "/bats_initial.pkl", "rb") as f:
    bats_initial_positions = pickle.load(f)
with open(history_output_dir + "/obstacles_initial.pkl", "rb") as f:
    obstacles_initial_positions = pickle.load(f)
with open(history_output_dir + "/jammers_initial.pkl", "rb") as f:
    jammers_initial_positions = pickle.load(f)

times = [i["time"] for i in list_containing_data_from_all_pickle_files]
sorting_indices = np.argsort(times)
list_containing_data_from_all_pickle_files = np.array(
    list_containing_data_from_all_pickle_files
)
list_containing_data_from_all_pickle_files = list_containing_data_from_all_pickle_files[
    sorting_indices
]

bat_positions = filter_bat_positions_from_history(
    list_containing_data_from_all_pickle_files
)
collision_rate = compute_collision_rate(bat_positions, parameter_df)
collision_counts = compute_collision_counts_and_length(bat_positions, parameter_df)

print(f"number of bats : {len(bat_positions[0])}")
print(f"time duration : {times[sorting_indices[-1]]}")
print(f"collision rate : {collision_rate}")
print(f"collsion counts : {collision_counts}")

time_ranges_to_check_saturation = np.arange(
    1000, len(list_containing_data_from_all_pickle_files), 1000
)
store_collision_counts = []
for x in time_ranges_to_check_saturation:
    _subset_history = list_containing_data_from_all_pickle_files[x:]
    _bat_positions = filter_bat_positions_from_history(_subset_history)
    collision_counts = compute_collision_counts_and_length(_bat_positions, parameter_df)
    store_collision_counts.append(collision_counts)

plt.plot(time_ranges_to_check_saturation, store_collision_counts)
plt.title("complementary cumulative plot of collision counts")
plt.ylabel("collision counts")
plt.xlabel("time x after which position data is considered")
plt.legend()
plt.show()

store_median_distances = []
for position_frame in bat_positions:
    distance_matrix = scp.spatial.distance_matrix(position_frame, position_frame)
    store_distances = []

    for i in range(distance_matrix.shape[0]):
        for j in range(distance_matrix.shape[0]):
            if i < j:
                store_distances.append(distance_matrix[i, j])

    store_median_distances.append(np.min(store_distances))

plt.plot(store_median_distances)
plt.title("median interbat distance with time")
plt.show()
