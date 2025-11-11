import bisect

import numpy as np


def str2bool(v):
    return v.lower() in ("yes", "true", "True", "t", "1")


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
        minimum_row_index = np.min(short_list_of_cells[:, 1])
        find_all_elements_with_min_row_index = [
            i for i in short_list_of_cells if i[0] == minimum_row_index
        ]
        pick_middle_element = int(
            np.floor(len(find_all_elements_with_min_row_index) / 2)
        )
        # pick_element_at_random = np.random.choice(
        #     range(len(find_all_elements_with_min_row_index))
        # )
        # output_cell_number = find_all_elements_with_min_row_index[
        #     pick_element_at_random
        # ]
        output_cell_number = find_all_elements_with_min_row_index[pick_middle_element]
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
        response_type = "repulsion"
    else:
        response_type = "attraction"

    next_direction = bat_direction.rotate(angle_of_next_direction)
    return next_direction.normalize(), response_type


def decide_next_direction_based_on_consistency(self, detected_sound_objects):
    """decide next direction of bat based on sound

    Args:
        detected_sound_objects (list): list containing detected sounds
    """
    len_cap_memory_window = self.parameters_df["MEMORY_WINDOW_FOR_CONSISTENCY"][0]
    number_of_consistent_ipis_for_behaviour = self.parameters_df[
        "NUMBER_OF_CONSISTENT_IPIS_FOR_MOVEMENT"
    ][0]
    grid_for_current_ipi, grid_row_labels, grid_column_labels = (
        convert_detected_sounds_into_grids(
            detected_sound_objects, self.parameters_df, self.allocentric_axis_y
        )
    )
    self.memory_window_to_store_grids.append(grid_for_current_ipi)

    length_of_memory_window = len(self.memory_window_to_store_grids)
    if length_of_memory_window > len_cap_memory_window:
        self.memory_window_to_store_grids.pop(0)
    elif length_of_memory_window <= len_cap_memory_window:
        number_of_consistent_ipis_for_behaviour = np.min(
            [number_of_consistent_ipis_for_behaviour, length_of_memory_window - 1]
        )

    grids_to_consider_for_direction_change = self.memory_window_to_store_grids.copy()
    sum_grids_in_memory = np.sum(grids_to_consider_for_direction_change, axis=0)

    cell_index_to_respond_to = given_matrix_find_cell_to_respond_to(
        sum_grids_in_memory, number_of_consistent_ipis_for_behaviour
    )

    if cell_index_to_respond_to is None:
        next_direction = self.direction
        response_type = None
    else:
        time_delay_of_activated_cell = grid_row_labels[cell_index_to_respond_to[0]]
        angle_of_activated_cell = grid_column_labels[cell_index_to_respond_to[1]]
        next_direction, response_type = given_time_and_angle_return_direction(
            time_delay_of_activated_cell,
            angle_of_activated_cell,
            self.parameters_df,
            self.direction,
            self.allocentric_axis_y,
        )

    return next_direction.normalize(), response_type


def decide_next_direction_based_on_loudest_sound(self, detected_sound_objects):
    """decide next direction of bat based on sound

    Args:
        detected_sound_objects (list): list containing detected sounds
    """
    effect_strength = np.pi
    spl_threshold_for_attractions = self.parameters_df["SPL_THRESHOLD_FOR_ATTRACTION"][
        0
    ]
    spl_threshold_for_repulsions = self.parameters_df["SPL_THRESHOLD_FOR_REPULSION"][0]
    if len(detected_sound_objects) != 0:
        max_spl = np.max([i["received_spl"] for i in detected_sound_objects])

        if max_spl > spl_threshold_for_attractions:

            max_spl_sound = [
                i for i in detected_sound_objects if i["received_spl"] == max_spl
            ][0]

            max_spl_sound_vector = self.generate_direction_vector_given_sound(
                max_spl_sound
            )

            if max_spl > spl_threshold_for_repulsions:
                next_direction = max_spl_sound_vector.rotate(np.pi).normalize()
                effect_strength = ((max_spl - spl_threshold_for_repulsions) / 5) * np.pi
                # print(f"Repulsion: {max_spl} dB")

            else:
                next_direction = max_spl_sound_vector.normalize()
                effect_strength = (
                    (max_spl - spl_threshold_for_attractions) / 5
                ) * np.pi
                # print(f"Attraction: {max_spl} dB")

        else:
            # Random direction change occasionally
            next_direction = self.generate_random_direction()

    else:
        # Random direction change occasionally
        next_direction = self.generate_random_direction()

    # put a cap on the max rotation based on spl
    cap_directon_change = effect_strength
    if self.direction.angle_between(next_direction) > cap_directon_change:
        next_direction = self.direction.rotate(cap_directon_change)
    elif self.direction.angle_between(next_direction) < -cap_directon_change:
        next_direction = self.direction.rotate(-cap_directon_change)

    return next_direction
