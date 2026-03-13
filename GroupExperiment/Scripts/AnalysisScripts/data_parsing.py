import glob
import multiprocessing
import os
import pickle
import sys
from itertools import product

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy as scp
import seaborn as sns

sys.path.append(
    "/home/adityamoger/Documents/GitHub/dynamic_model_of_cocktail_party_nightmare/dynamic_model/"
)

from scores.collision_scores import compute_collision_counts_and_length
from scores.run_all_score_calculations import filter_bat_positions_from_history
from supporting_files.utilities import load_history_dump, load_parameters


def single_bat_collision_counts(bat_positions, parameters_df):

    # bat_positions = [i["bat_positions"] for i in history][5000:]

    arena_width = parameters_df["ARENA_WIDTH"]
    arena_length = parameters_df["ARENA_LENGTH"]
    bat_radius = parameters_df["BAT_RADIUS"]

    collision_counter = 0
    wall_collision_counter = 0
    batbat_collision_counter = 0
    # collision_duration = []
    track_collision_in_last_frame_w_bats = []
    track_collision_in_last_frame_w_walls = []

    store_individual_scores_wall = np.zeros(
        shape=(len(bat_positions), len(bat_positions[0]))
    )
    store_individual_scores_batbat = np.zeros(
        shape=(len(bat_positions), len(bat_positions[0]))
    )
    # duration_tracker = np.zeros(shape=(len(bat_positions), len(bat_positions)))

    for frame_number, position_frame in enumerate(bat_positions):
        distance_matrix = scp.spatial.distance_matrix(position_frame, position_frame)

        track_collision_in_current_frame_w_bats = []
        track_collision_in_current_frame_w_walls = []

        for i in range(distance_matrix.shape[0]):
            for j in range(distance_matrix.shape[0]):
                if i < j:
                    if distance_matrix[i, j] < 2 * bat_radius:
                        track_collision_in_current_frame_w_bats.append((i, j))
                        if (i, j) not in track_collision_in_last_frame_w_bats:
                            collision_counter += 1
                            batbat_collision_counter += 1
                            store_individual_scores_batbat[frame_number][i] += 1
                            store_individual_scores_batbat[frame_number][j] += 1

        for i, bat in enumerate(position_frame):

            if (
                bat[0] >= arena_width - bat_radius
                or bat[0] <= bat_radius
                or bat[1] >= arena_length - bat_radius
                or bat[1] <= bat_radius
            ):
                track_collision_in_current_frame_w_walls.append(i)

                if i not in track_collision_in_last_frame_w_walls:
                    collision_counter += 1
                    wall_collision_counter += 1
                    store_individual_scores_wall[frame_number][i] += 1

        track_collision_in_last_frame_w_bats = track_collision_in_current_frame_w_bats
        track_collision_in_last_frame_w_walls = track_collision_in_current_frame_w_walls

    return (
        collision_counter,
        wall_collision_counter,
        batbat_collision_counter,
        np.sum(store_individual_scores_wall, axis=0),
        np.sum(store_individual_scores_batbat, axis=0),
    )


def given_folder_find_bat_positions(history_output_dir):
    list_of_dict_files = glob.glob(history_output_dir + "/history_dump_*.pkl")
    list_of_dict_files = np.sort(list_of_dict_files)

    list_containing_data_from_all_pickle_files = []
    for pickle_file in list_of_dict_files:
        with open(pickle_file, "rb") as f:
            _list_containing_subset = pickle.load(f)
            list_containing_data_from_all_pickle_files.extend(_list_containing_subset)

    # parameter_file = glob.glob(history_output_dir + "/parameters_used.json")[0]
    # parameter_df = load_parameters(parameter_file)

    times = [i["time"] for i in list_containing_data_from_all_pickle_files]
    sorting_indices = np.argsort(times)
    list_containing_data_from_all_pickle_files = np.array(
        list_containing_data_from_all_pickle_files
    )
    list_containing_data_from_all_pickle_files = (
        list_containing_data_from_all_pickle_files[sorting_indices]
    )

    bat_positions = filter_bat_positions_from_history(
        list_containing_data_from_all_pickle_files
    )
    del list_containing_data_from_all_pickle_files
    return bat_positions


big_output_dir = "/media/adityamoger/T7 Shield/BACKUP_THESIS_DATA"
treatment_dir = big_output_dir + "/*_treatment"
null_dir = big_output_dir + "/*_null"
consistency_types = ["", "_2_3"]
experiment_types = ["positive_control", "negative_control", "treatment", "null"]
group_sizes = [5, 10, 30, 50, 75, 100]
iterations = np.arange(0, 20, 1)

store_scores_labels = [
    (
        "experiment_type",
        "group_size",
        "iteration",
        "collision_counts",
        "wall_collision_counts",
        "bat_bat_collision_counts",
        "duration",
        "consistency_type",
    )
]
store_individual_scores_labels = [
    (
        "experiment_type",
        "group_size",
        "iteration",
        "collision_counts",
        "wall_collision_counts",
        "bat_bat_collision_counts",
        "duration",
        "consistency_type",
        "bat_id",
    )
]


# for experiment_type in experiment_types:
#     for i, group_size in enumerate(group_sizes):
#         for iteration in iterations:
#             history_file_dir = big_output_dir+f"/*_{experiment_type}"+f"/*_{i}"+f"/*_{iteration}"
#             history_file_dir = glob.glob(history_file_dir)[0]
#             bat_positions = given_folder_find_bat_positions(history_file_dir)
#             parameter_file = glob.glob(history_file_dir + "/parameters_used.json")[0]
#             parameter_df = load_parameters(parameter_file)
#             collision_counts, wall_collision_counts, bat_bat_collision_counts = compute_collision_counts_and_length(bat_positions, parameter_df)
#             store_scores.append((experiment_type, group_size, iteration, collision_counts, wall_collision_counts, bat_bat_collision_counts, len(bat_positions)))

# with open("condensed_data_0_1.pickle", "wb") as output_file:
#     pickle.dump(store_scores, output_file)


def parse_given_params(experiment_type, iteration, group_size, consistency_type):
    i = group_sizes.index(group_size)
    # folder_name = experiment_type + consistency_type

    history_file_dir = (
        big_output_dir
        + f"/*_{experiment_type+consistency_type}"
        + f"/*_{i}"
        + f"/*_{iteration}"
    )
    try:
        history_file_dir = glob.glob(history_file_dir)[0]
    except IndexError:
        print(
            f"error for files; {(experiment_type, iteration, group_size, consistency_type)}"
        )
        raise IndexError("KILL YOURSELF")
    bat_positions = given_folder_find_bat_positions(history_file_dir)
    parameter_file = glob.glob(history_file_dir + "/parameters_used.json")[0]
    parameter_df = load_parameters(parameter_file)
    store_scores, store_individual_scores = [], []
    (
        collision_counts,
        wall_collision_counts,
        bat_bat_collision_counts,
        individual_scores_wall,
        individual_scores_batbat,
    ) = single_bat_collision_counts(bat_positions, parameter_df)

    consistency_value = "2/3" if consistency_type == "_2_3" else "3/5"
    store_scores.append(
        (
            experiment_type,
            group_size,
            iteration,
            collision_counts,
            wall_collision_counts,
            bat_bat_collision_counts,
            len(bat_positions) / 1000,
            consistency_value,
        )
    )
    # print(store_scores)
    # print(
    #     (
    #         experiment_type,
    #         group_size,
    #         iteration,
    #         collision_counts,
    #         wall_collision_counts,
    #         bat_bat_collision_counts,
    #         len(bat_positions) / 1000,
    #         consistency_value,
    #     )
    # )

    for i in range(len(individual_scores_wall)):
        sum_collision_counts = individual_scores_wall[i] + individual_scores_batbat[i]
        store_individual_scores.append(
            (
                experiment_type,
                group_size,
                iteration,
                sum_collision_counts,
                individual_scores_wall[i],
                individual_scores_batbat[i],
                len(bat_positions) / 1000,
                consistency_value,
                i,
            )
        )

    print(
        f"done for params; {experiment_type, iteration, group_size, consistency_type}"
    )
    del bat_positions
    return store_scores, store_individual_scores


for groupsize in group_sizes:

    array_of_param_values = [
        experiment_types,
        iterations,
        [groupsize],
        consistency_types,
    ]
    list_of_combinations = list(product(*array_of_param_values))

    num_processes = 10 if groupsize > 50 else 20

    with multiprocessing.Pool(processes=num_processes) as pool:
        value1 = pool.starmap(parse_given_params, list_of_combinations)
        # print(value1)

    for item in value1:
        store_scores_labels.append(item[0][0])
        store_individual_scores_labels.extend(item[1])

    with open(
        f"group_size_{groupsize}_condensed_data_whole.pickle", "wb"
    ) as output_file:
        pickle.dump(store_scores_labels, output_file)

    with open(
        f"group_size_{groupsize}_condensed_data_whole_individual_based.pickle", "wb"
    ) as output_file:
        pickle.dump(store_individual_scores_labels, output_file)
