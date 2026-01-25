"""These are misc functions that are used across many files"""

import bisect
import json
import os
import pickle

import numpy as np
import pandas as pd
from supporting_files.vectors import Vector


def make_dir(directory):
    """makes directory if the folder doesnt exist

    Args:
        directory (string): directory that needs to be made
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def convert_txt_to_int_or_float(txt):
    """convert a string to int if it can be made into an int.

    Args:
        txt (string): string to attempt conversion

    Returns:
        string/ int: is int if it can be converted else string
    """
    try:
        k = float(txt)
        if k % 1 == 0:
            return int(k)
        return k

    except ValueError:
        return txt


# def load_parameters(file_dir):
#     """load parameters from csv

#     Args:
#         file_dir (string): directory of the csv file

#     Returns:
#         DataFrame: DataFrame extracted from csv file
#     """
#     with open(file_dir, "r") as csv_file:
#         reader = pd.read_csv(file_dir)
#     # output_df = pd.DataFrame({})
#     # for key in reader.keys():
#     #     value = reader[key][0]
#     #     value = convert_txt_to_int_or_float(value)
#     #     output_df[key] = [value]
#     return reader


def load_parameters(file_dir):
    """load parameters from json

    Args:
        file_dir (string): directory of the csv file

    Returns:
        DataFrame: DataFrame extracted from csv file
    """
    with open(file_dir) as f:
        output_df = json.load(f)
    # with open(file_dir, "r") as csv_file:
    #     reader = pd.read_csv(file_dir)
    # output_df = pd.DataFrame({})
    # for key in reader.keys():
    #     value = reader[key][0]
    #     value = convert_txt_to_int_or_float(value)
    #     output_df[key] = [value]
    return output_df


def call_directionality_factor(a, theta):
    """Calculates the drop in source level as the angle
    increases from on-axis.

    The function calculates the drop using the third term
    in equation 11 of Giuggioli et al. 2015

    Args:
        A (float >0): Asymmetry parameter
        theta (float): Angle at which the call directionality factor is
                to be calculated in radians. 0 radians is on-axis.
    Returns:

        float <=0: The amount of drop in dB which occurs when the call is measured off-axis.
    """
    if a < 0:
        raise ValueError("A should be >0 ! ")

    call_dirn = a * (np.cos(theta) - 1)

    return call_dirn


def creation_time_calculation(sound, reflection_point):
    """calculate the creation time of a echo given reflection point

    Args:
        sound (DirectSound): sound object generating the reflection
        reflection_point (Vector): point of generation of echosound

    Returns:
        float: time of creation of echo
    """
    distance_from_sound_origin = (sound.origin - reflection_point).magnitude()
    speed_of_sound = sound.speed
    time_taken = distance_from_sound_origin / speed_of_sound
    time_of_creation_of_echo = time_taken + sound.creation_time
    return time_of_creation_of_echo


def combine_pickle_files(directory_path):
    combined_df = pd.DataFrame(
        {}
    )  # Initialize an empty DataFrame to store the merged data

    for file_name in os.listdir(directory_path):
        if file_name.endswith(".pickle"):
            print(file_name)
            file_path = os.path.join(directory_path, file_name)
            with open(file_path, "rb") as f:
                content = pd.DataFrame.from_dict(pickle.load(f))

                if isinstance(content, pd.DataFrame):
                    combined_df = pd.concat([combined_df, content], ignore_index=True)

    return combined_df


def make_vector(tuple):
    # makes vector object
    vectorized_tuple = Vector(x=tuple[0], y=tuple[1])
    return vectorized_tuple


def str2bool(v):
    return v.lower() in ("yes", "true", "True", "t", "1")


def change_tuples_to_vector_in_sound(sound):
    keys_to_rebuild = [
        "sound_direction",
        "incident_direction",
        "bat_direction",
        "bat_position",
    ]
    for key in keys_to_rebuild:
        if isinstance(sound[key], Vector):
            continue
        sound[key] = make_vector(sound[key])

    return sound


def load_history_dump(filename):
    data = np.load(filename)
    times = data["times"]
    bat_counts = data["bat_counts"]
    positions_flat = data["positions"]

    reconstructed_history = []
    pos_index = 0

    for i, n_bats in enumerate(bat_counts):
        frame_positions = []
        for bat_idx in range(n_bats):
            x = positions_flat[pos_index]
            y = positions_flat[pos_index + 1]
            frame_positions.append((x, y))
            pos_index += 2

        reconstructed_history.append(
            {"time": float(times[i]), "bat_positions": frame_positions}
        )

    return reconstructed_history


def read_temporal_masking_fn(dir):
    dict_1 = pd.read_csv(dir)
    dict_2 = {}
    for key in dict_1.keys()[1:]:
        dict_2[key] = np.float64(dict_1[key].values)
    return dict_2
