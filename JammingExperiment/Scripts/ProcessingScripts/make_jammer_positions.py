import numpy as np
from agents.class_jammers import Jammers
from supporting_files.vectors import Vector


def make_jammers(parameters_df):

    jammer_resolution = parameters_df["JAMMER_RESOLUTION"]
    call_rate = parameters_df["CALL_RATE"]
    width_array = np.arange(
        jammer_resolution,
        parameters_df["ARENA_WIDTH"],
        jammer_resolution,
    )
    length_array = np.arange(
        jammer_resolution,
        parameters_df["ARENA_LENGTH"],
        jammer_resolution,
    )

    left_wall = [Vector(0, i) for i in length_array]
    right_wall = [Vector(parameters_df["ARENA_WIDTH"], i) for i in length_array]
    top_wall = [Vector(i, parameters_df["ARENA_LENGTH"]) for i in width_array]
    bottom_wall = [Vector(i, 0) for i in width_array]

    left_jammer_directions = [Vector(1, 0) for i in left_wall]
    right_jammer_directions = [Vector(-1, 0) for i in right_wall]
    top_jammer_directions = [Vector(0, -1) for i in top_wall]
    bottom_jammer_directions = [Vector(0, 1) for i in bottom_wall]

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
