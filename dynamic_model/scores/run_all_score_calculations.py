import glob
import os

import numpy as np
import pandas as pd
from scores.calling_effort_score import calling_effort
from scores.collision_scores_single_bat import (
    compute_collision_counts_and_length,
    compute_collision_rate,
)
from scores.space_occupied_scores import space_occupied_score


def load_history_dump(folder_path):
    """Load and merge all history dump files in a folder by time order"""

    pattern = os.path.join(folder_path, "history_dump_*.npz")
    npz_files = glob.glob(pattern)

    if not npz_files:
        print(f"No history dump files found in {folder_path}")
        return []

    # extract timestamps from filenames and sort by time
    file_times = []
    for file_path in npz_files:
        try:

            filename = os.path.basename(file_path)
            time_str = filename.replace("history_dump_", "").replace(".npz", "")
            timestamp = float(time_str)
            file_times.append((timestamp, file_path))
        except ValueError:
            print(f"could not parse timestamp from filename: {filename}")
            continue

    file_times.sort(key=lambda x: x[0])
    all_frames = []

    for timestamp, file_path in file_times:
        # print(f"Loading: {os.path.basename(file_path)} (time: {timestamp})")

        data = np.load(file_path)
        times = data["times"]
        positions_array = data["positions"]
        # call_times_array = data["bat_call_time"]
        for i, frame_time in enumerate(times):
            frame_data = positions_array[i]
            valid_positions = frame_data[~np.isnan(frame_data)]
            bat_positions = np.array(
                [
                    (valid_positions[j], valid_positions[j + 1])
                    for j in range(0, len(valid_positions), 2)
                ]
            )
            # bat_call_time = np.array([])

            all_frames.append(
                {
                    "time": np.round(frame_time, 3),
                    "bat_positions_x": bat_positions[:, 0],
                    "bat_positions_y": bat_positions[:, 1],
                    # "bat_call_time": bat_call_time
                }
            )
    all_frames.sort(key=lambda x: x["time"])
    return all_frames


def filter_bat_positions_from_history(all_frames):

    store_only_positions = []
    for item in all_frames:
        store_only_positions.append(item["bat_positions"])
    return store_only_positions


def reformat_history(history, focal_bat, parameter_df, iteration_label):
    # get time, position, call time data
    # reformat into long csv
    subset_of_focal_bat = []
    for item in history:
        reformatted_item = {
            "time": item["time"],
            "bat_position_x": item["bat_positions"][focal_bat][0],
            "bat_position_y": item["bat_positions"][focal_bat][1],
            "bat_call_time": item["bat_call_time"][focal_bat],
            "iteration_number": iteration_label,
        }
        reformatted_item.update(parameter_df.copy())
        subset_of_focal_bat.append(reformatted_item)

    # df_position_data = pd.DataFrame.from_dict(subset_of_focal_bat, orient="columns")
    # print(df_position_data)
    return subset_of_focal_bat


def take_history_store_scores(sim, sim_iteration_number):
    focal_bat = sim.bats[0]
    bat_positions = filter_bat_positions_from_history(sim.history)

    space_occupied = space_occupied_score(sim.parameters_df, bat_positions)
    collision_counts = compute_collision_counts_and_length(
        bat_positions, sim.parameters_df
    )
    collision_rate = compute_collision_rate(bat_positions, sim.parameters_df)
    calling_effort_score = calling_effort(focal_bat)

    dict_to_store = {
        "space_occupied": space_occupied,
        "collision_counts": collision_counts,
        "collision_rate": collision_rate,
        "calling_effort": calling_effort_score,
        "iteration_label": sim_iteration_number,
    }
    dict_to_store.update(sim.parameters_df)

    return dict_to_store
