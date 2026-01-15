import numpy as np
from agents.class_obstacles import Obstacle
from supporting_files.vectors import Vector


class WallPanel(Obstacle):
    def __init__(self, parameters_df, position):
        radius = 0.0001
        super().__init__(parameters_df, position, radius)

    def __repr__(self):
        return f"WallPanel(id={self.id}, position={self.position})"


def make_walls(parameters_df):
    width_array = np.arange(
        parameters_df["WALL_RESOLUTION"][0],
        parameters_df["ARENA_WIDTH"][0],
        parameters_df["WALL_RESOLUTION"][0],
    )
    height_array = np.arange(
        parameters_df["WALL_RESOLUTION"][0],
        parameters_df["ARENA_HEIGHT"][0],
        parameters_df["WALL_RESOLUTION"][0],
    )
    # positions_to_put_objects = []
    left_wall = [(0, i) for i in height_array]
    right_wall = [(parameters_df["ARENA_WIDTH"][0], i) for i in height_array]
    top_wall = [(i, parameters_df["ARENA_HEIGHT"][0]) for i in width_array]
    bottom_wall = [(i, 0) for i in width_array]
    positions_to_put_objects = [*left_wall, *right_wall, *top_wall, *bottom_wall]
    # object_labels =
    # positions_to_put_objects = [* for i in walls]

    store_wall_objects = [
        WallPanel(parameters_df, position) for position in positions_to_put_objects
    ]
    return store_wall_objects
