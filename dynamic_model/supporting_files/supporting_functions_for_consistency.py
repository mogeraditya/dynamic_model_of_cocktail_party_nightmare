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


def check_if_two_lists_are_disjoint(list1, list2):
    for element in list1:
        is_element_in_list2 = any(
            all(item in sublist for item in element) for sublist in list2
        )
        if is_element_in_list2:
            return False
    return True


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


def given_matrix_find_cell_to_respond_to_presence(
    matrix, threshold_for_activation, previous_output_cell
):
    find_all_elements_with_min_row_index, find_all_thresholds_with_min_row_index = (
        given_matrix_shortlist_response_cells(matrix, threshold_for_activation)
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


def given_matrix_find_cell_to_respond_to_absence(
    matrix,
    threshold_for_activation,
    parameters_df,
    columns,
    bat_direction,
    allocentric_axis_y,
):
    # need to output the cell that corresponds to direction of the bat
    find_all_elements_with_min_row_index = given_matrix_shortlist_response_cells(
        matrix, threshold_for_activation
    )[0]

    _first_element_for_nan_check = find_all_elements_with_min_row_index[0][0]
    if np.isnan(_first_element_for_nan_check):
        return [np.nan, np.nan]

    spatial_reference_frame = parameters_df["SPATIAL_REFERENCE_FRAME"][0]

    if spatial_reference_frame == "allocentric":
        angle_between_self_and_allocentric_axis = bat_direction.angle_between(
            allocentric_axis_y
        )
    elif spatial_reference_frame == "egocentric":
        angle_between_self_and_allocentric_axis = 0
    else:
        raise ValueError("incorrect reference frame choice")

    column_index_of_direction = bisect.bisect_right(
        columns, angle_between_self_and_allocentric_axis
    )

    row_index_of_activation = find_all_elements_with_min_row_index[0][0]
    column_indices_having_activations = find_all_elements_with_min_row_index[:, 1]
    column_indices_not_having_activations = np.array(
        [
            i
            for i in range(1, matrix.shape[1])
            if i not in column_indices_having_activations
        ]
    )
    print(
        np.degrees(angle_between_self_and_allocentric_axis), column_index_of_direction
    )
    print(column_indices_having_activations, column_indices_not_having_activations)
    if column_index_of_direction in column_indices_not_having_activations:
        return [row_index_of_activation, column_index_of_direction]
    elif len(column_indices_not_having_activations) == 0:
        return [row_index_of_activation, column_index_of_direction]
    else:
        nearest_empty_column_index = column_indices_not_having_activations[
            np.abs(
                column_indices_not_having_activations - column_index_of_direction
            ).argmin()
        ]
        print([row_index_of_activation, nearest_empty_column_index])
        return [row_index_of_activation, nearest_empty_column_index]


def given_parameters_df_return_grid_matrix_zeros(parameters_df):
    radial_resolution = parameters_df["BAT_RADIAL_RESOLUTION"][0]
    angular_resolution = np.radians(parameters_df["BAT_ANGULAR_RESOLUTION"][0])
    call_duration = parameters_df["CALL_DURATION"][0]
    post_call_sampling_interval = parameters_df["TIME_DELAY_FOR_DIRECTION_CHANGE"][0]

    spatial_grid_r = np.arange(
        call_duration, post_call_sampling_interval, radial_resolution
    )
    spatial_grid_theta = np.arange(-np.pi, np.pi, angular_resolution)
    matrix_spatial_grid = np.zeros(shape=(len(spatial_grid_r), len(spatial_grid_theta)))
    return matrix_spatial_grid, spatial_grid_r, spatial_grid_theta


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

    if len(heard_sounds) == 0:
        return store_grid, spatial_grid_r, spatial_grid_theta
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
    if (store_grid == matrix_spatial_grid).all():
        print("aiyo")
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
    controller_type = parameters_df["CONTROLLER_TYPE"][0]

    angular_resolution = np.radians(parameters_df["BAT_ANGULAR_RESOLUTION"][0])
    radial_resolution = parameters_df["BAT_RADIAL_RESOLUTION"][0]
    noise_in_angle = np.random.uniform(-angular_resolution / 2, angular_resolution / 2)
    angle_of_next_direction = (
        angle_of_activated_cell + angular_resolution / 2 + noise_in_angle
    )
    corrected_time_delay = time_delay_of_activated_cell + radial_resolution / 2

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
            response_type = "attraction"
    elif controller_type == "absence":
        print(np.degrees(angle_of_next_direction))
        response_type = "repulsion"
    else:
        raise ValueError("unsupported controller type")

    next_direction = bat_direction.rotate(angle_of_next_direction)
    return next_direction.normalize(), response_type


def implement_absence_tracker():
    # goal is to implement a code st bat goes towards regions lcking sound.
    return None
