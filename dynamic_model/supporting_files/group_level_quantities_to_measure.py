import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import scipy as scp

sys.path.append("./dynamic_model")
from simulation_and_plotting.plotter import stitch_together_history_lists


# implement collision rate
def compute_collision_rate(history):
    # bat positions
    bat_positions = [i["bat_positions"] for i in history]
    # compute distance matrix in allf rames
    number_of_collisions_across_time = []
    for position_frame in bat_positions:
        distance_matrix = scp.spatial.distance_matrix(position_frame, position_frame)
        count_collisions = (
            np.sum([distance_matrix < 0.25]) - distance_matrix.shape[0]
        ) / 2
        number_of_collisions_across_time.append(count_collisions)

    return np.sum(number_of_collisions_across_time)

def compute_median_interindividual_distance()

if __name__ == "__main__":
    print(os.getcwd())
    OUTPUT_DIR = r"./test_intelligent_movement_12bats_nice_rotations/data_for_plotting/"
    SAVE_ANIMATION = False  # OUTPUT_DIR
    history, parameters_df, bats, obstacles = stitch_together_history_lists(OUTPUT_DIR)
    # plt.plot(compute_collision_rate(history))
    # plt.show()
    print(compute_collision_rate(history))
