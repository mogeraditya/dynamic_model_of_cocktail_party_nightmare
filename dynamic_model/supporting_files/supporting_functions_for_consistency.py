import bisect

import numpy as np
from supporting_files.utilities import str2bool


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


# def check_if_two_lists_are_disjoint(list1, list2):
#     for element in list1:
#         is_element_in_list2 = any(
#             all(item in sublist for item in element) for sublist in list2
#         )
#         if is_element_in_list2:
#             return False
#     return True


def given_matrix_shortlist_response_cells(matrix, threshold_for_activation):
    num_rows, num_columns = matrix.shape
    short_list_of_cells = []
    short_listed_thresholds = []
    for i in range(num_rows):
        for j in range(num_columns):
            if matrix[i, j] >= threshold_for_activation:
                short_list_of_cells.append([i, j])
                short_listed_thresholds.append(matrix[i, j])

    short_list_of_cells = np.array(short_list_of_cells)
    short_listed_thresholds = np.array(short_listed_thresholds)

    find_all_elements_with_min_row_index = []
    find_all_thresholds_with_min_row_index = []

    if len(short_list_of_cells) == 0:
        find_all_thresholds_with_min_row_index.append([np.nan, np.nan])
        find_all_elements_with_min_row_index.append([np.nan, np.nan])
    else:

        np.random.shuffle(short_list_of_cells)
        minimum_row_index = np.min(short_list_of_cells[:, 0])

        for i, matrix_index in enumerate(short_list_of_cells):
            if matrix_index[0] == minimum_row_index:
                find_all_elements_with_min_row_index.append(matrix_index)
                find_all_thresholds_with_min_row_index.append(
                    short_listed_thresholds[i]
                )

    return (
        np.array(find_all_elements_with_min_row_index),
        find_all_thresholds_with_min_row_index,
    )


def given_parameters_df_return_grid_matrix_zeros(parameters_df):
    radial_resolution = parameters_df["BAT_RADIAL_RESOLUTION"]
    angular_resolution = np.radians(parameters_df["BAT_ANGULAR_RESOLUTION"])
    call_duration = parameters_df["CALL_DURATION"]
    post_call_sampling_interval = parameters_df["TIME_DELAY_FOR_DIRECTION_CHANGE"]

    spatial_grid_r = np.arange(
        call_duration,
        post_call_sampling_interval + radial_resolution,
        radial_resolution,
    )
    spatial_grid_theta = np.arange(-np.pi, np.pi, angular_resolution)
    matrix_spatial_grid = np.zeros(shape=(len(spatial_grid_r), len(spatial_grid_theta)))
    return matrix_spatial_grid, spatial_grid_r, spatial_grid_theta


def convert_detected_sounds_into_grids(
    heard_sounds, parameters_df, bat_direction, allocentric_axis_y
):
    """

    Args:
        heard_sounds (_type_): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """

    spatial_reference_frame = parameters_df["SPATIAL_REFERENCE_FRAME"]
    convert_grid_to_one_hot = str2bool(parameters_df["CONVERT_GRIDS+TO_ONE_HOT_?"])
    time_step_size = parameters_df["TIME_STEP"]
    rounding_based_on_time_step = len(str(time_step_size).split(".")[1])

    matrix_spatial_grid, spatial_grid_r, spatial_grid_theta = (
        given_parameters_df_return_grid_matrix_zeros(parameters_df)
    )
    store_grid = matrix_spatial_grid.copy()

    if len(heard_sounds) == 0:
        return store_grid, spatial_grid_r, spatial_grid_theta
    for sound_object in heard_sounds:

        delta_t = (
            np.array(sound_object["occurance_times"])[0]
            - sound_object["bat_last_call_time"]
        )
        delta_t = np.round(delta_t, rounding_based_on_time_step)
        # print(sound_object)

        if spatial_reference_frame == "allocentric":
            theta = allocentric_axis_y.angle_between(sound_object["incident_direction"])
        elif spatial_reference_frame == "egocentric":
            theta = bat_direction.angle_between(sound_object["incident_direction"])
        else:
            raise ValueError("not a supported spatial reference frame")

        grid_row_index = bisect.bisect_left(spatial_grid_r, delta_t)
        grid_column_index = bisect.bisect_left(spatial_grid_theta, theta)

        # angles are circular
        if grid_column_index == len(spatial_grid_theta):
            grid_column_index = 0

        store_grid[grid_row_index, grid_column_index] += 1
    if convert_grid_to_one_hot:
        store_grid = convert_matrix_to_one_hot(store_grid).copy()
    else:
        store_grid = store_grid / np.max(store_grid)
    return store_grid, spatial_grid_r, spatial_grid_theta


def given_time_and_angle_return_direction(
    time_delay_of_activated_cell,
    angle_of_activated_cell,
    parameters_df,
    bat_direction,
    allocentric_axis_y,
):
    spatial_reference_frame = parameters_df["SPATIAL_REFERENCE_FRAME"]
    time_delay_threshold_for_repulsion = parameters_df[
        "TIME_DELAY_THRESHOLD_FOR_REPULSION"
    ]
    controller_type = parameters_df["CONTROLLER_TYPE"]

    angular_resolution = np.radians(parameters_df["BAT_ANGULAR_RESOLUTION"])
    radial_resolution = parameters_df["BAT_RADIAL_RESOLUTION"]
    noise_in_angle = np.random.uniform(-angular_resolution / 2, angular_resolution / 2)
    angle_of_next_direction = (
        angle_of_activated_cell - angular_resolution / 2 + noise_in_angle
    )
    corrected_time_delay = time_delay_of_activated_cell - radial_resolution / 2

    if spatial_reference_frame == "allocentric":
        angle_between_self_and_allocentric_axis = bat_direction.angle_between(
            allocentric_axis_y
        )
        angle_of_next_direction += angle_between_self_and_allocentric_axis

    if controller_type == "presence":
        if corrected_time_delay <= time_delay_threshold_for_repulsion:
            angle_of_next_direction += np.pi
            response_type = "repulsion"
        else:
            # print(f"attraction delay{corrected_time_delay}")
            response_type = "attraction"
    elif controller_type == "absence":
        # print(np.degrees(angle_of_next_direction))
        response_type = "repulsion"
    else:
        raise ValueError("unsupported controller type")

    next_direction = bat_direction.rotate(angle_of_next_direction)
    return next_direction.normalize(), response_type


def given_angle_find_cell_priorities(angle, columns):
    difference_array = np.abs(np.array(columns) - angle)
    sorting_order = np.argsort(difference_array)
    return sorting_order


def find_indices_corresponding_to_hearing_range(
    parameters_df,
    spatial_grid_theta,
    angle_between_reference_axis_and_bat,
    hearing_range,
):
    bat_angular_resolution = np.radians(parameters_df["BAT_ANGULAR_RESOLUTION"])

    # print(hearing_range, angle_between_reference_axis_and_bat)
    angles_to_hearing_range = np.arange(
        -hearing_range + angle_between_reference_axis_and_bat,
        hearing_range
        + angle_between_reference_axis_and_bat
        + bat_angular_resolution / 2,
        bat_angular_resolution,
    )
    angles_to_hearing_range = convert_angles_to_negpi_to_pi(angles_to_hearing_range)
    indices_corresponding_to_hearing_range = [
        bisect.bisect_left(spatial_grid_theta, i) for i in angles_to_hearing_range
    ]
    indices_corresponding_to_hearing_range = [
        i if i != len(spatial_grid_theta) else 0
        for i in indices_corresponding_to_hearing_range
    ]
    # print(f"angles in hearing range {np.degrees(np.array(angles_to_hearing_range))}")
    return indices_corresponding_to_hearing_range


def check_if_no_sound_in_front_of_bat(
    matrix,
    angle_between_reference_axis_and_bat,
    number_of_consistent_ipis_for_behaviour,
    parameters_df,
):
    matrix_w_only_activations = np.zeros(shape=matrix.shape)
    indices_of_matrix_w_activations = np.where(
        matrix >= number_of_consistent_ipis_for_behaviour
    )
    matrix_w_only_activations[indices_of_matrix_w_activations] = 1
    consolidated_matrix = np.sum(matrix_w_only_activations, axis=0)

    angular_resolution = np.radians(parameters_df["BAT_ANGULAR_RESOLUTION"])
    spatial_grid_theta = np.arange(-np.pi, np.pi, angular_resolution)

    frontal_range_indices = find_indices_corresponding_to_hearing_range(
        parameters_df,
        spatial_grid_theta,
        angle_between_reference_axis_and_bat,
        hearing_range=np.radians(parameters_df["BAT_FRONTAL_RANGE"]),
    )

    sublist_based_on_frontal_range = []
    for index in frontal_range_indices:
        sublist_based_on_frontal_range.append(consolidated_matrix[index])

    if all(i == 0 for i in sublist_based_on_frontal_range):
        return True
    else:
        return False


def make_sublist_based_on_hearing_range(
    activation_array, angle_between_reference_axis_and_bat, parameters_df
):
    angular_resolution = np.radians(parameters_df["BAT_ANGULAR_RESOLUTION"])
    spatial_grid_theta = np.arange(-np.pi, np.pi, angular_resolution)

    hearing_range = np.radians(parameters_df["HEARING_ANGLE_THRESHOLD"])
    hearing_range_indices = find_indices_corresponding_to_hearing_range(
        parameters_df,
        spatial_grid_theta,
        angle_between_reference_axis_and_bat,
        hearing_range,
    )

    sublist_based_on_hearing_range = []
    for index in hearing_range_indices:
        sublist_based_on_hearing_range.append(activation_array[index])

    return np.array(sublist_based_on_hearing_range), np.array(hearing_range_indices)


def convert_angles_to_negpi_to_pi(list_of_angles):
    new_list = []
    for angle in list_of_angles:
        if angle > np.pi or angle < -np.pi:
            opposite_sign = np.sign(angle) * -1
            converted_angle = angle % (opposite_sign * np.pi)
        else:
            converted_angle = angle
        new_list.append(converted_angle)
    return np.array(new_list)


def given_matrix_find_cell_to_respond_to_presence(
    matrix,
    number_of_consistent_ipis_for_behaviour,
    parameters_df,
    bat_direction,
    allocentric_axis_y,
    previous_output_cell,
):
    angle_between_reference_axis_and_bat = allocentric_axis_y.angle_between(
        bat_direction
    )

    no_consistent_sound_in_front = check_if_no_sound_in_front_of_bat(
        matrix,
        angle_between_reference_axis_and_bat,
        number_of_consistent_ipis_for_behaviour,
        parameters_df,
    )
    if no_consistent_sound_in_front:
        # print()
        return [np.nan, np.nan]

    find_all_elements_with_min_row_index, find_all_thresholds_with_min_row_index = (
        given_matrix_shortlist_response_cells(
            matrix, number_of_consistent_ipis_for_behaviour
        )
    )

    _first_element_for_nan_check = find_all_elements_with_min_row_index[0][0]
    if np.isnan(_first_element_for_nan_check):
        return [np.nan, np.nan]
    else:
        is_previous_cell_repeated = any(
            all(item in sublist for item in previous_output_cell)
            for sublist in find_all_elements_with_min_row_index
        )

        if is_previous_cell_repeated:
            return previous_output_cell

        output_cell_number = find_all_elements_with_min_row_index[
            np.argsort(find_all_thresholds_with_min_row_index)[-1]
        ]
        return output_cell_number
