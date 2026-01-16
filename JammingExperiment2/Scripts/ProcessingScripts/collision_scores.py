import glob
import os

import numpy as np
import scipy as scp


def load_history_dump(folder_path):
    """Load and merge all history dump files in a folder by time order"""
    # Find all npz files in the folder
    pattern = os.path.join(folder_path, "history_dump_*.npz")
    npz_files = glob.glob(pattern)

    if not npz_files:
        print(f"No history dump files found in {folder_path}")
        return []

    # Extract timestamps from filenames and sort by time
    file_times = []
    for file_path in npz_files:
        try:
            # Extract timestamp from filename: history_dump_123.446.npz
            filename = os.path.basename(file_path)
            time_str = filename.replace("history_dump_", "").replace(".npz", "")
            timestamp = float(time_str)
            file_times.append((timestamp, file_path))
        except ValueError:
            # print(f"Could not parse timestamp from filename: {filename}")
            continue

    # Sort files by timestamp
    file_times.sort(key=lambda x: x[0])

    all_frames = []

    # Load and merge all files in time order
    for timestamp, file_path in file_times:
        # print(f"Loading: {os.path.basename(file_path)} (time: {timestamp})")

        data = np.load(file_path)
        times = data["times"]
        positions_array = data["positions"]  # 2D array: [frames, max_bats*2]

        # Reconstruct frames from this file
        for i, frame_time in enumerate(times):
            frame_data = positions_array[i]
            # Remove NaN values and pair x,y coordinates
            valid_positions = frame_data[~np.isnan(frame_data)]
            bat_positions = [
                (valid_positions[j], valid_positions[j + 1])
                for j in range(0, len(valid_positions), 2)
            ]

            all_frames.append(
                {"time": np.round(frame_time, 3), "bat_positions": bat_positions}
            )

    # Sort all frames by time to ensure correct time series
    all_frames.sort(key=lambda x: x["time"])

    # print(f"Loaded {len(all_frames)} frames from {len(file_times)} files")
    store_only_positions = []
    for item in all_frames:
        store_only_positions.append(item["bat_positions"])
    return store_only_positions


def compute_collision_rate(bat_positions, parameters_df):
    # bat positions
    # bat_positions =
    # compute distance matrix in allf rames
    arena_width = parameters_df["ARENA_WIDTH"][0]
    arena_LENGTH = parameters_df["ARENA_LENGTH"][0]
    bat_radius = parameters_df["BAT_RADIUS"][0]

    number_of_collisions_across_time = []
    for position_frame in bat_positions:
        distance_matrix = scp.spatial.distance_matrix(position_frame, position_frame)
        count_collisions = (
            np.sum([distance_matrix < bat_radius * 2]) - distance_matrix.shape[0]
        ) / 2
        for bat in position_frame:
            if bat[0] >= arena_width - bat_radius or bat[0] <= bat_radius:
                count_collisions += 1
            elif bat[1] >= arena_LENGTH - bat_radius or bat[1] <= bat_radius:
                count_collisions += 1
        number_of_collisions_across_time.append(count_collisions)

    return np.sum(number_of_collisions_across_time) / len(bat_positions)


def compute_collision_counts_and_length(bat_positions, parameters_df):
    # bat_positions = [i["bat_positions"] for i in history][1000:]

    arena_width = parameters_df["ARENA_WIDTH"][0]
    arena_LENGTH = parameters_df["ARENA_LENGTH"][0]
    bat_radius = parameters_df["BAT_RADIUS"][0]

    collision_counter = 0
    collision_duration = []
    track_collision_in_last_frame_w_bats = []
    track_collision_in_last_frame_w_walls = []

    duration_tracker = np.zeros(shape=(len(bat_positions), len(bat_positions)))

    for position_frame in bat_positions:
        distance_matrix = scp.spatial.distance_matrix(position_frame, position_frame)

        track_collision_in_current_frame_w_bats = []
        track_collision_in_current_frame_w_walls = []

        for i in range(distance_matrix.shape[0]):
            for j in range(distance_matrix.shape[0]):
                if i < j:
                    if distance_matrix[i, j] < 2 * bat_radius:
                        track_collision_in_current_frame_w_bats.append((i, j))
                        if (i, j) not in track_collision_in_last_frame_w_bats:
                            collision_counter += 1

        for i, bat in enumerate(position_frame):

            if (
                bat[0] >= arena_width - bat_radius
                or bat[0] <= bat_radius
                or bat[1] >= arena_LENGTH - bat_radius
                or bat[1] <= bat_radius
            ):
                track_collision_in_current_frame_w_walls.append(i)

                if i not in track_collision_in_last_frame_w_walls:
                    collision_counter += 1

        track_collision_in_last_frame_w_bats = track_collision_in_current_frame_w_bats
        track_collision_in_last_frame_w_walls = track_collision_in_current_frame_w_walls

    return collision_counter


def time_spent_in_collision(bat_positions, parameters_df):
    arena_width = parameters_df["ARENA_WIDTH"][0]
    arena_LENGTH = parameters_df["ARENA_LENGTH"][0]
    bat_radius = parameters_df["BAT_RADIUS"][0]

    collision_list = []
    for position_frame in bat_positions:
        distance_matrix = scp.spatial.distance_matrix(position_frame, position_frame)
        count_collisions = (
            np.sum([distance_matrix < 0.24]) - distance_matrix.shape[0]
        ) / 2
        for bat in position_frame:
            if bat[0] >= arena_width - bat_radius or bat[0] <= bat_radius:
                count_collisions += 1
            elif bat[1] >= arena_LENGTH - bat_radius or bat[1] <= bat_radius:
                count_collisions += 1

        if count_collisions != 0:
            collision_list.append(1)
        else:
            collision_list.append(0)
        # track_collision_in_last_frame_w_bats = track_collision_in_current_frame_w_bats
        # track_collision_in_last_frame_w_walls = track_collision_in_current_frame_w_walls
    return collision_list, np.sum(collision_list)


def individual_collision_rate(bat_positions, parameters_df):

    arena_width = parameters_df["ARENA_WIDTH"][0]
    arena_LENGTH = parameters_df["ARENA_LENGTH"][0]
    bat_radius = parameters_df["BAT_RADIUS"][0]

    individual_rate = []
    number_of_bats = len(bat_positions[0])
    for bat in range(0, number_of_bats):
        for position_frame in bat_positions:
            # for bat in position_frame:
            if (
                position_frame[bat][0] >= arena_width - bat_radius
                or position_frame[bat][0] <= bat_radius
            ):
                count_collisions += 1
            elif (
                position_frame[bat][1] >= arena_LENGTH - bat_radius
                or position_frame[bat][1] <= bat_radius
            ):
                count_collisions += 1
