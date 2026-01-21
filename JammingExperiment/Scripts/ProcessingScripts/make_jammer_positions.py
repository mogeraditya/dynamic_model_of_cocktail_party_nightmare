import numpy as np

from dynamic_model.agents.class_jammers import Jammers


def make_jammer_locations(parameters_df, jammer_resolution, call_rate):
    arena_width = parameters_df["ARENA_WIDTH"][0]
    arena_length = parameters_df["ARENA_LENGTH"][0]

    width_array = np.arange(
        jammer_resolution,
        parameters_df["ARENA_WIDTH"][0],
        jammer_resolution,
    )
    length_array = np.arange(
        jammer_resolution,
        parameters_df["ARENA_LENGTH"][0],
        jammer_resolution,
    )

    left_wall = [(0, i) for i in length_array]
    right_wall = [(parameters_df["ARENA_WIDTH"][0], i) for i in length_array]
    top_wall = [(i, parameters_df["ARENA_LENGTH"][0]) for i in width_array]
    bottom_wall = [(i, 0) for i in width_array]

    left_jammer_directions = [(1, 0) for i in left_wall]
    right_jammer_directions = [(-1, 0) for i in right_wall]
    top_jammer_directions = [(0, -1) for i in top_wall]
    bottom_jammer_directions = [(0, 1) for i in bottom_wall]

    positions_to_put_jammers = [*left_wall, *right_wall, *top_wall, *bottom_wall]
    directions_of_jammers = [
        *left_jammer_directions,
        *right_jammer_directions,
        *top_jammer_directions,
        *bottom_jammer_directions,
    ]
    wall_ids = [
        *["left_wall"] * len(left_wall),
        *["right_wall"] * len(right_wall),
        *["top_wall"] * len(top_wall),
        *["bottom_wall"] * len(bottom_wall),
    ]

    store_wall_objects = [
        Jammers(
            parameters_df, position, directions_of_jammers[i], call_rate, wall_ids[i]
        )
        for i, position in enumerate(positions_to_put_jammers)
    ]
    return store_wall_objects
