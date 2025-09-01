"""These are misc functions that are used across many files"""

import os
import pickle

import numpy as np
import pandas as pd


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


def load_parameters(file_dir):
    """load parameters from csv

    Args:
        file_dir (string): directory of the csv file

    Returns:
        DataFrame: DataFrame extracted from csv file
    """
    with open(file_dir, "r") as csv_file:
        reader = pd.read_csv(csv_file)
    output_df = pd.DataFrame()
    for key in reader.keys():
        value = reader[key][0]
        value = convert_txt_to_int_or_float(value)
        output_df[key] = [value]
    return output_df


def call_directionality_factor(A, theta):
    """Calculates the drop in source level as the angle
    increases from on-axis.

    The function calculates the drop using the third term
    in equation 11 of Giuggioli et al. 2015

     Parameters
    ----------
    A : float >0. Asymmetry parameter
    theta : float. Angle at which the call directionality factor is
            to be calculated in radians. 0 radians is on-axis.
      Returns
    -------

    call_dirn : float <=0. The amount of drop in dB which occurs when the call
                is measured off-axis.
    """
    if A <= 0:
        raise ValueError("A should be >0 ! ")

    call_dirn = A * (np.cos(theta) - 1)

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
    combined_df = (
        pd.DataFrame()
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
