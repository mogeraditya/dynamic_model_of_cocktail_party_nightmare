import numpy as np
import scipy as scp


def compute_collision_rate(bat_positions, parameters_df):

    arena_width = parameters_df["ARENA_WIDTH"]
    arena_length = parameters_df["ARENA_LENGTH"]
    bat_radius = parameters_df["BAT_RADIUS"]

    number_of_collisions_across_time = []
    for position_frame in bat_positions:
        count_collisions = 0
        for bat in position_frame:
            if bat[0] >= (arena_width - bat_radius) or bat[0] <= bat_radius:
                count_collisions += 1
            elif bat[1] >= (arena_length - bat_radius) or bat[1] <= bat_radius:
                count_collisions += 1
        number_of_collisions_across_time.append(count_collisions)

    return np.sum(number_of_collisions_across_time) / len(bat_positions)


def compute_collision_counts_and_length(bat_positions, parameters_df):
    # bat_positions = [i["bat_positions"] for i in history][1000:]

    arena_width = parameters_df["ARENA_WIDTH"]
    arena_length = parameters_df["ARENA_LENGTH"]
    bat_radius = parameters_df["BAT_RADIUS"]

    collision_counter = 0
    # collision_duration = []
    track_collision_in_last_frame_w_walls = []

    # duration_tracker = np.zeros(shape=(len(bat_positions), len(bat_positions)))

    for position_frame in bat_positions:

        track_collision_in_current_frame_w_walls = []

        for i, bat in enumerate(position_frame):

            if (
                bat[0] >= arena_width - bat_radius
                or bat[0] <= bat_radius
                or bat[1] >= arena_length - bat_radius
                or bat[1] <= bat_radius
            ):
                track_collision_in_current_frame_w_walls.append(i)

                if i not in track_collision_in_last_frame_w_walls:
                    collision_counter += 1

        track_collision_in_last_frame_w_walls = track_collision_in_current_frame_w_walls

    return collision_counter


def time_spent_in_collision(bat_positions, parameters_df):
    arena_width = parameters_df["ARENA_WIDTH"]
    arena_length = parameters_df["ARENA_LENGTH"]
    bat_radius = parameters_df["BAT_RADIUS"]

    collision_list = []
    for position_frame in bat_positions:
        count_collisions = 0
        for bat in position_frame:
            if bat[0] >= arena_width - bat_radius or bat[0] <= bat_radius:
                count_collisions += 1
            elif bat[1] >= arena_length - bat_radius or bat[1] <= bat_radius:
                count_collisions += 1

        if count_collisions != 0:
            collision_list.append(1)
        else:
            collision_list.append(0)

    return np.sum(collision_list)
