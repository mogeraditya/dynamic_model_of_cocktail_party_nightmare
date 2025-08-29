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


def compute_median_interindividual_distance(history):
    bat_positions = [i["bat_positions"] for i in history]
    # compute distance matrix in allf rames
    distances_array = []

    for position_frame in bat_positions:
        distance_matrix = scp.spatial.distance_matrix(position_frame, position_frame)
        inter_bat_distances_given_frame = []
        for i in range(distance_matrix.shape[0]):
            for j in range(distance_matrix.shape[0]):
                if i < j:
                    inter_bat_distances_given_frame.append(distance_matrix[i, j])
        distances_array.append(inter_bat_distances_given_frame)

    return distances_array


if __name__ == "__main__":
    print(os.getcwd())
    OUTPUT_DIR = r"./test_intelligent_movement_25bats_final_epic/data_for_plotting/"
    SAVE_ANIMATION = False  # OUTPUT_DIR
    history, parameters_df, bats, obstacles = stitch_together_history_lists(OUTPUT_DIR)
    # plt.plot(compute_collision_rate(history))
    # plt.show()
    print(compute_collision_rate(history))
    median_array = np.median(compute_median_interindividual_distance(history), axis=1)
    plt.plot(median_array)
    plt.show()
