import glob
import os

import numpy as np
import pandas as pd


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

        for i, frame_time in enumerate(times):
            frame_data = positions_array[i]
            valid_positions = frame_data[~np.isnan(frame_data)]
            bat_positions = np.array(
                [
                    (valid_positions[j], valid_positions[j + 1])
                    for j in range(0, len(valid_positions), 2)
                ]
            )

            all_frames.append(
                {
                    "time": np.round(frame_time, 3),
                    "bat_positions_x": bat_positions[:, 0],
                    "bat_positions_y": bat_positions[:, 1],
                }
            )
    all_frames.sort(key=lambda x: x["time"])
    return all_frames


def filter_bat_positions_from_history(all_frames):

    store_only_positions = []
    for item in all_frames:
        store_only_positions.append((item["bat_positions_x"], item["bat_positions_y"]))
    return store_only_positions


def reformat_history(all_frames, focal_bat):
    # get time, position, call time data
    # reformat into long csv
    subset_of_focal_bat = []

    df_position_data = pd.DataFrame.from_dict(all_frames)
