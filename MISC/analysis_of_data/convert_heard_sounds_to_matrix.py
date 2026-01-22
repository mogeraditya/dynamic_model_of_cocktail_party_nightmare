import bisect
import glob
import os
import pickle
import sys

import matplotlib as mpl
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Arrow, Circle, Patch, Rectangle, Wedge

sys.path.append("./analysis_of_data/")
sys.path.append("./exploratory_analysis/")
sys.path.append("./dynamic_model/")


from read_simulation_output import read_data_per_simulation_per_bat
from snr_implementation import parse_sounds, serialize_sound_info

plt.style.use("dark_background")
sys.path.append("./dynamic_model")
plt.rcParams["animation.ffmpeg_path"] = "/usr/bin/ffmpeg"
ANGULAR_RESOLUTION = np.pi / 18  # radians
RADIAL_RESOLUTION = 0.001
param = (0, True, np.pi)


def generate_heard_sounds_array(directory, focal_bat, parameters_df):
    azimuth = parameters_df["HEARING_ANGLE_THRESHOLD"]
    num_bats = parameters_df["NUM_BATS"]
    time_threshold_post_call = parameters_df["TIME_DELAY_FOR_DIRECTION_CHANGE"]

    output_dir = directory + f"/{focal_bat}/"
    received_sounds_sorted_by_time, time_of_call_emissions = (
        read_data_per_simulation_per_bat(output_dir, "received")
    )
    # print(received_sounds_sorted_by_time)
    if len(received_sounds_sorted_by_time) == 0:
        raise ValueError("empty dir")

    list_of_heard_sounds = []
    for i, frame in enumerate(received_sounds_sorted_by_time):
        heard_sounds = parse_sounds(
            frame,
            time_threshold_post_call=time_threshold_post_call,
            angle_threshold=azimuth,
            focal_bat=focal_bat,
            include_direct_sounds=True,
        )
        heard_sounds = serialize_sound_info(heard_sounds)
        list_of_heard_sounds.append(heard_sounds)
    return list_of_heard_sounds, time_of_call_emissions


def generate_matrix_array(directory, focal_bat, parameters_df):
    azimuth = parameters_df["HEARING_ANGLE_THRESHOLD"]
    num_bats = parameters_df["NUM_BATS"]
    time_threshold_post_call = parameters_df["TIME_DELAY_FOR_DIRECTION_CHANGE"]

    output_dir = directory + f"/{focal_bat}/"
    received_sounds_sorted_by_time, time_of_call_emissions = (
        read_data_per_simulation_per_bat(output_dir, "ipi_matrix")
    )
    # print(received_sounds_sorted_by_time)
    if len(received_sounds_sorted_by_time) == 0:
        raise ValueError("empty dir")

    # list_of_heard_sounds = []
    # for i, frame in enumerate(received_sounds_sorted_by_time):
    #     heard_sounds = parse_sounds(
    #         frame,
    #         time_threshold_post_call=time_threshold_post_call,
    #         angle_threshold=azimuth,
    #         focal_bat=focal_bat,
    #         include_direct_sounds=True,
    #     )
    #     heard_sounds = serialize_sound_info(heard_sounds)
    #     list_of_heard_sounds.append(heard_sounds)

    return received_sounds_sorted_by_time, time_of_call_emissions


def convert_into_grids(heard_sounds_array, focal_bat, parameters_df):
    time_threshold_post_call = parameters_df["TIME_DELAY_FOR_DIRECTION_CHANGE"]
    duration_of_call = parameters_df["CALL_DURATION"]
    spatial_grid_r = np.arange(
        duration_of_call, time_threshold_post_call, RADIAL_RESOLUTION
    )
    spatial_grid_theta = np.arange(-np.pi, np.pi, ANGULAR_RESOLUTION)
    matrix_spatial_grid = np.zeros(shape=(len(spatial_grid_r), len(spatial_grid_theta)))

    counter = 0
    store_grids = [
        matrix_spatial_grid.copy(),
    ]
    for i, frame_heard_sounds in enumerate(heard_sounds_array):
        # store_grids = [matrix_spatial_grid.copy()]*3
        for sound_object in frame_heard_sounds:

            delta_t = (
                np.array(sound_object["occurance_times"])[0]
                - sound_object["bat_last_call_time"]
            )
            theta = sound_object["bat_direction"].angle_between(
                sound_object["incident_direction"]
            )

            grid_row_index = bisect.bisect_right(spatial_grid_r, delta_t) - 1
            grid_column_index = bisect.bisect_right(spatial_grid_theta, theta) - 1
            # print(FOCAL_BAT, sound_object["emitter_id"])
            if sound_object["emitter_id"] == focal_bat:

                index_for_storage = 0
                counter += 1
            else:
                raise ValueError("shouldnt have any other sound")
            # print(grid_row_index, grid_column_index)
            # if theta>-np.pi and theta<-5*np.pi/6:
            #     print(theta)
            store_grids[index_for_storage][grid_row_index, grid_column_index] += 1

    return store_grids, spatial_grid_r, spatial_grid_theta


def convert_into_grids_time_series(
    heard_sounds_array, focal_bat, parameters_df, time_series_of_call_emission
):

    time_threshold_post_call = parameters_df["TIME_DELAY_FOR_DIRECTION_CHANGE"]
    duration_of_call = parameters_df["CALL_DURATION"]
    spatial_grid_r = np.arange(
        duration_of_call, time_threshold_post_call, RADIAL_RESOLUTION
    )
    spatial_grid_theta = np.arange(-np.pi, np.pi, ANGULAR_RESOLUTION)
    matrix_spatial_grid = np.zeros(shape=(len(spatial_grid_r), len(spatial_grid_theta)))

    time_series_of_simulation = np.arange(
        0, parameters_df["SIM_DURATION"], parameters_df["TIME_STEP"]
    )

    store_grid_time_series = []
    counter = 0
    for time_step in time_series_of_simulation:
        if time_step < time_series_of_call_emission[0]:
            store_grid_time_series.append([matrix_spatial_grid.copy()])
            print(time_step)
            continue
        # print(time_series_of_call_emission, time_step)
        ipi_number = np.where(time_series_of_call_emission <= time_step)[0][-1]
        frame_heard_sounds = heard_sounds_array[ipi_number]
        # store_grids = [matrix_spatial_grid.copy()]*3
        store_grids = [matrix_spatial_grid.copy()]
        for sound_object in frame_heard_sounds:

            delta_t = (
                np.array(sound_object["occurance_times"])[0]
                - sound_object["bat_last_call_time"]
            )
            theta = sound_object["bat_direction"].angle_between(
                sound_object["incident_direction"]
            )

            grid_row_index = bisect.bisect_right(spatial_grid_r, delta_t) - 1
            grid_column_index = bisect.bisect_right(spatial_grid_theta, theta) - 1

            if sound_object["emitter_id"] == focal_bat:
                index_for_storage = 0
                counter += 1
            else:
                raise ValueError("shouldnt have any other sound")
            # print(grid_row_index, grid_column_index)
            # if theta>-np.pi and theta<-5*np.pi/6:
            #     print(theta)
            store_grids[index_for_storage][grid_row_index, grid_column_index] += 1

        store_grid_time_series.append(store_grids)
    # print(store_grid_time_series[0:10])
    return np.array(store_grid_time_series), spatial_grid_r, spatial_grid_theta


def convert_matrix_for_plotting_nicer(
    list_of_matrix, rows, columns, increase_resolution_by, focal_bat
):  #:( plot nice banane ke liye
    list_of_matrix = list_of_matrix[focal_bat : focal_bat + 1]
    angular_resolution = columns[1] - columns[0]
    new_angular_resolution = angular_resolution / increase_resolution_by
    new_column_labels = np.arange(-np.pi, np.pi, new_angular_resolution)[::-1]
    # print(list_of_matrix)
    # print(new_matrix.shape)
    new_list_of_matrix = []
    # print([i.shape for i in list_of_matrix])
    # print(list_of_matrix[0])
    for matrix in list_of_matrix:
        # print(matrix)
        # print(matrix.shape)
        new_matrix = np.zeros(shape=(len(rows), len(new_column_labels) - 1)).copy()
        for i in range(new_matrix.shape[0]):
            for j in range(new_matrix.shape[1]):
                index_in_old_matrix = i, j // increase_resolution_by
                # print(index_in_old_matrix)
                # print(new_matrix)
                # print(matrix)
                new_matrix[i, j] = matrix[index_in_old_matrix]

        new_list_of_matrix.append(new_matrix)

    return new_list_of_matrix, new_angular_resolution


# def convert_matrix_for_plotting_nicer(
#     list_of_matrix, rows, columns, increase_resolution_by
# ):  #:( plot nice banane ke liye
#     angular_resolution = columns[1] - columns[0]
#     new_angular_resolution = angular_resolution / increase_resolution_by
#     new_column_labels = np.arange(-np.pi, np.pi, new_angular_resolution)
#     # print(list_of_matrix)
#     # print(new_matrix.shape)
#     new_list_of_matrix = []
#     # print([i.shape for i in list_of_matrix])
#     # print(list_of_matrix[0])
#     # for matrix in list_of_matrix:
#     matrix = list_of_matrix
#     new_matrix = np.zeros(shape=(len(rows), len(new_column_labels) - 1)).copy()
#     for i in range(new_matrix.shape[0]):
#         for j in range(new_matrix.shape[1]):
#             index_in_old_matrix = i, j // increase_resolution_by
#             # print(index_in_old_matrix)
#             # print(new_matrix)
#             print(matrix)
#             new_matrix[i, j] = matrix[index_in_old_matrix]

#     new_list_of_matrix.append(new_matrix)

#     return new_list_of_matrix, new_angular_resolution
