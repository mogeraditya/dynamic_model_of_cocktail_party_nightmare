import bisect

import numpy as np


def space_occupied_score(parameters_df, bat_positions):
    # TODO : make this multi bat compatible.
    arena_width = parameters_df["ARENA_WIDTH"][0]
    arena_length = parameters_df["ARENA_LENGTH"][0]

    x = np.arange(0, arena_width, 0.5)
    y = np.arange(0, arena_length, 0.5)

    track_unique_cells = []
    for bat_position_frame in bat_positions:
        grid_x_index = bisect.bisect_left(x, bat_position_frame[0][0])
        grid_y_index = bisect.bisect_left(y, bat_position_frame[0][1])
        grid_cell_identity = str([grid_x_index, grid_y_index])

        if grid_cell_identity not in track_unique_cells:
            track_unique_cells.append(grid_cell_identity)
    total_cells = len(x) * len(y)
    fraction_space_occupied = len(track_unique_cells) / total_cells

    return fraction_space_occupied, len(track_unique_cells)


# if __name__ == "__main__":
#     parameters_df = {"ARENA_WIDTH": [10], "ARENA_LENGTH": [10]}
#     bat_positions =
