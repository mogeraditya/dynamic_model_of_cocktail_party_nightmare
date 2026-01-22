import numpy as np
from agents.class_obstacles import Obstacle
from supporting_files.vectors import Vector


class WallPanel(Obstacle):
    def __init__(self, parameters_df, position, wall_id):
        radius = 0.0001
        super().__init__(parameters_df, position, radius)
        self.wall_id = wall_id

    def __repr__(self):
        return f"WallPanel(id={self.id}, position={self.position})"


def make_walls(parameters_df):
    width_array = np.arange(
        parameters_df["WALL_RESOLUTION"],
        parameters_df["ARENA_WIDTH"],
        parameters_df["WALL_RESOLUTION"],
    )
    length_array = np.arange(
        parameters_df["WALL_RESOLUTION"],
        parameters_df["ARENA_LENGTH"],
        parameters_df["WALL_RESOLUTION"],
    )

    left_wall = [(0, i) for i in length_array]
    right_wall = [(parameters_df["ARENA_WIDTH"], i) for i in length_array]
    top_wall = [(i, parameters_df["ARENA_LENGTH"]) for i in width_array]
    bottom_wall = [(i, 0) for i in width_array]
    positions_to_put_objects = [*left_wall, *right_wall, *top_wall, *bottom_wall]
    wall_ids = [
        *["left_wall"] * len(left_wall),
        *["right_wall"] * len(right_wall),
        *["top_wall"] * len(top_wall),
        *["bottom_wall"] * len(bottom_wall),
    ]

    store_wall_objects = [
        WallPanel(parameters_df, position, wall_ids[i])
        for i, position in enumerate(positions_to_put_objects)
    ]
    return store_wall_objects
