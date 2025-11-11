import numpy as np
from supporting_files.utilities import (
    convert_detected_sounds_into_grids,
    given_matrix_find_cell_to_respond_to,
    given_time_and_angle_return_direction,
)


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
