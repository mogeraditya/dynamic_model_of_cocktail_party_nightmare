"""These are misc functions that are used across many files"""

import bisect
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

    Args:
        A (float >0): Asymmetry parameter
        theta (float): Angle at which the call directionality factor is
                to be calculated in radians. 0 radians is on-axis.
    Returns:

        float <=0: The amount of drop in dB which occurs when the call is measured off-axis.
    """
    if A < 0:
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
        sound[key] = make_vector(sound[key])

    return sound


def convert_matrix_to_one_hot(matrix):
    one_hot_matrix = matrix.copy()
    num_rows, num_columns = matrix.shape
    for i in range(num_rows):
        for j in range(num_columns):
            if matrix[i, j] > 0:
                one_hot_matrix[i, j] = 1
            else:
                one_hot_matrix[i, j] = 0
    return one_hot_matrix


def given_matrix_find_cell_to_respond_to(matrix, threshold_for_activation):
    # cell_to_respond_to =
    num_rows, num_columns = matrix.shape
    short_list_of_cells = []
    for i in range(num_rows):
        for j in range(num_columns):
            if matrix[i, j] >= threshold_for_activation:
                short_list_of_cells.append([i, j])
    short_list_of_cells = np.array(short_list_of_cells)
    if len(short_list_of_cells) == 0:
        return None
    else:
        minimum_row_index = np.min(short_list_of_cells[:, 0])
        find_all_elements_with_min_row_index = [
            i for i in short_list_of_cells if i[0] == minimum_row_index
        ]
        pick_element_at_random = np.random.choice(
            range(len(find_all_elements_with_min_row_index))
        )
        output_cell_number = find_all_elements_with_min_row_index[
            pick_element_at_random
        ]
        return output_cell_number


def convert_detected_sounds_into_grids(heard_sounds, parameters_df, allocentric_axis_y):
    """

    Args:
        heard_sounds (_type_): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    radial_resolution = parameters_df["BAT_RADIAL_RESOLUTION"][0]
    angular_resolution = np.radians(parameters_df["BAT_ANGULAR_RESOLUTION"][0])
    call_duration = parameters_df["CALL_DURATION"][0]
    post_call_sampling_interval = parameters_df["TIME_DELAY_FOR_DIRECTION_CHANGE"][0]
    spatial_reference_frame = parameters_df["SPATIAL_REFERENCE_FRAME"][0]
    convert_grid_to_one_hot = str2bool(parameters_df["CONVERT_GRIDS+TO_ONE_HOT_?"][0])

    spatial_grid_r = np.arange(
        call_duration, post_call_sampling_interval, radial_resolution
    )
    spatial_grid_theta = np.arange(-np.pi, np.pi, angular_resolution)
    matrix_spatial_grid = np.zeros(shape=(len(spatial_grid_r), len(spatial_grid_theta)))

    store_grid = matrix_spatial_grid.copy()

    for sound_object in heard_sounds:

        delta_t = (
            np.array(sound_object["occurance_times"])[0]
            - sound_object["bat_last_call_time"]
        )

        if spatial_reference_frame == "allocentric":
            theta = allocentric_axis_y.angle_between(sound_object["incident_direction"])
        elif spatial_reference_frame == "egocentric":
            theta = sound_object["bat_direction"].angle_between(
                sound_object["incident_direction"]
            )
        else:
            raise ValueError("not a supported spatail reference frame")

        grid_row_index = bisect.bisect_right(spatial_grid_r, delta_t) - 1
        grid_column_index = bisect.bisect_right(spatial_grid_theta, theta) - 1

        store_grid[grid_row_index, grid_column_index] += 1
    if convert_grid_to_one_hot:
        store_grid = convert_matrix_to_one_hot(store_grid).copy()

    return store_grid, spatial_grid_r, spatial_grid_theta


def given_time_and_angle_return_direction(
    time_delay_of_activated_cell,
    angle_of_activated_cell,
    parameters_df,
    bat_direction,
    allocentric_axis_y,
):
    spatial_reference_frame = parameters_df["SPATIAL_REFERENCE_FRAME"][0]
    time_delay_threshold_for_repulsion = parameters_df[
        "TIME_DELAY_THRESHOLD_FOR_REPULSION"
    ][0]

    angular_resolution = np.radians(parameters_df["BAT_ANGULAR_RESOLUTION"][0])
    radial_resolution = parameters_df["BAT_RADIAL_RESOLUTION"][0]

    angle_of_next_direction = angle_of_activated_cell + angular_resolution / 2
    corrected_time_delay = time_delay_of_activated_cell + radial_resolution / 2

    if spatial_reference_frame == "allocentric":
        angle_between_self_and_allocentric_axis = bat_direction.angle_between(
            allocentric_axis_y
        )
        angle_of_next_direction += angle_between_self_and_allocentric_axis

    if corrected_time_delay <= time_delay_threshold_for_repulsion:
        angle_of_next_direction += np.pi

    next_direction = bat_direction.rotate(angle_of_next_direction)
    return next_direction.normalize()
