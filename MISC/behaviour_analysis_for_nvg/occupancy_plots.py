import glob
import os
import pickle
import sys

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Arrow, Circle, Patch, Rectangle, Wedge

sys.path.append("./dynamic_model")
plt.rcParams["animation.ffmpeg_path"] = "/usr/bin/ffmpeg"


def stitch_together_history_lists(history_output_dir):
    """Merges lists from all the pickle files together.

    Args:
        history_output_dir (string):

    Returns:
        list: list with all the merged lists from pickle files.
    """
    list_of_dict_files = glob.glob(history_output_dir + "/history_dump_*.pkl")
    list_of_dict_files = np.sort(list_of_dict_files)
    # print(list_of_dict_files)
    list_containing_data_from_all_pickle_files = []
    for pickle_file in list_of_dict_files:
        with open(pickle_file, "rb") as f:
            _list_containing_subset = pickle.load(f)
            list_containing_data_from_all_pickle_files.extend(_list_containing_subset)

    parameter_file = glob.glob(history_output_dir + "/parameters_used.pkl")[0]
    parameter_df = pd.read_pickle(parameter_file)
    with open(history_output_dir + "/bats_initial.pkl", "rb") as f:
        bats_initial_positions = pickle.load(f)
    with open(history_output_dir + "/obstacles_initial.pkl", "rb") as f:
        obstacles_initial_positions = pickle.load(f)
    times = [i["time"] for i in list_containing_data_from_all_pickle_files]
    sorting_indices = np.argsort(times)
    list_containing_data_from_all_pickle_files = np.array(
        list_containing_data_from_all_pickle_files
    )
    list_containing_data_from_all_pickle_files = (
        list_containing_data_from_all_pickle_files[sorting_indices]
    )
    # print(len(list_containing_data_from_all_pickle_files))
    # print(times)
    return (
        list_containing_data_from_all_pickle_files,
        parameter_df,
        bats_initial_positions,
        obstacles_initial_positions,
    )


def given_history_make_list_of_positions(history):
    list_of_bat_positions = []
    for frame in history:
        bat_position = frame["bat_positions"][0]
        list_of_bat_positions.append(bat_position)
    list_of_bat_positions = np.array(list_of_bat_positions)
    return list_of_bat_positions


def read_multiple_iterations(output_dir, dir_to_store, name):
    folders_in_parameter = np.sort(glob.glob(output_dir + "/*"))[0:6]
    dict_w_values = {}
    dict_w_values["positions"] = []
    dict_w_values["iteration"] = []
    for iteration_folder in folders_in_parameter:
        history, parameters_df = stitch_together_history_lists(
            iteration_folder + "/data_for_plotting/"
        )[0:2]
        positions = given_history_make_list_of_positions(history)
        dict_w_values["positions"].extend(positions)
        dict_w_values["iteration"].extend([iteration_folder] * len(positions))
        print(iteration_folder)
    with open(dir_to_store + f"{name}_data.pickle", "wb") as handle:
        pickle.dump(dict_w_values, handle, protocol=pickle.HIGHEST_PROTOCOL)
    dict_w_values["positions"] = np.array(dict_w_values["positions"])
    return dict_w_values


if __name__ == "__main__":
    # print(os.getcwd())
    OUTPUT_DIR = r"./consistency_of_calls_movement_rule_data/2_of_5/data_for_plotting/"  # "/media/adityamoger/T7 Shield/dir_store_snr/NVG_effect_of_consistency_metric/2_out_of_5/iteration_number_0/data_for_plotting"
    bat_locations_dir = "./behaviour_analysis_for_nvg/bat_start_positions.csv"
    obstacle_locations_dir = "./behaviour_analysis_for_nvg/chain_positions.csv"

    bat_locations = pd.read_csv(bat_locations_dir)
    obstacle_locations = pd.read_csv(obstacle_locations_dir)
    x = stitch_together_history_lists(OUTPUT_DIR)
    list_of_bat_positions = []
    for frame in x[0]:
        bat_position = frame["bat_positions"][0]
        list_of_bat_positions.append(bat_position)
    list_of_bat_positions = np.array(list_of_bat_positions)
    plt.scatter(
        list_of_bat_positions[:, 0][::10],
        list_of_bat_positions[:, 1][::10],
        alpha=0.2,
        color="green",
    )
    plt.scatter(obstacle_locations["x"], obstacle_locations["y"], color="red")
    plt.show()

    # OUTPUT_DIR = "/media/adityamoger/T7 Shield/dir_store_snr/NVG_effect_of_consistency_metric/2_out_of_5/"
    # bat_locations_dir = "./behaviour_analysis_for_nvg/bat_start_positions.csv"
    # obstacle_locations_dir = "./behaviour_analysis_for_nvg/chain_positions.csv"

    # bat_locations = pd.read_csv(bat_locations_dir)
    # obstacle_locations = pd.read_csv(obstacle_locations_dir)
    # dict_w_values = read_multiple_iterations(OUTPUT_DIR, "", "2_out_of_5")
    # plt.scatter(
    #     dict_w_values["positions"][:, 0][::100],
    #     dict_w_values["positions"][:, 1][::100],
    #     alpha=0.02,
    #     color="green",
    # )
    # plt.scatter(obstacle_locations["x"], obstacle_locations["y"], color="red")
    # plt.show()
