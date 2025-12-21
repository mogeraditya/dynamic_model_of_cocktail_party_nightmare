import numpy as np
from agents.obstacles import Obstacle


def make_walls(parameters_df):
    width_array = np.arange(
        0.5, parameters_df["ARENA_WIDTH"][0], parameters_df["WALL_RESOLUTION"][0]
    )
    height_array = np.arange(
        0.5, parameters_df["ARENA_HEIGHT"][0], parameters_df["WALL_RESOLUTION"][0]
    )
    # positions_to_put_objects = []
    left_wall = [(0, i) for i in height_array]
    right_wall = [(parameters_df["ARENA_WIDTH"][0], i) for i in height_array]
    top_wall = [(i, parameters_df["ARENA_HEIGHT"][0]) for i in width_array]
    bottom_wall = [(i, 0) for i in width_array]
    positions_to_put_objects = [*left_wall, *right_wall, *top_wall, *bottom_wall]
    # object_labels =
    # positions_to_put_objects = [* for i in walls]

    obstacle_radius = 0.0001
    store_wall_objects = [
        Obstacle(parameters_df, position, obstacle_radius)
        for position in positions_to_put_objects
    ]
    return store_wall_objects
