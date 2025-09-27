import sys

import matplotlib.pyplot as plt
import numpy as np
from snr_implementation import given_sound_objects_return_detected_sounds

sys.path.append("./dynamic_model")
from read_simulation_output import read_data_per_simulation_per_bat
from supporting_files.utilities import make_dir

NUM_COLORS = 50
TEMPORAL_MASKING_DIR = "./exploratory_analysis/temporal_masking_fn.csv"
AZIMUTHS = [np.pi, np.pi / 2, np.pi / 6]
TIME_THRESHOLDS = [0.035]
INCLUDE_DIRECT_SOUNDS = True


for TIME_THRESHOLD in TIME_THRESHOLDS:
    for AZIMUTH in AZIMUTHS:
        for FOCAL_BAT in [1, 27, 35]:
            OUTPUT_DIR = f"./dump_files/snr_{NUM_COLORS}_bats_with_directional_calls/{FOCAL_BAT}/"
            received_sounds_sorted_by_time = read_data_per_simulation_per_bat(
                OUTPUT_DIR, "received"
            )

            cm = plt.get_cmap("gist_rainbow")

            plt.figure(figsize=(60, 10))
            plt.style.use("dark_background")

            for frame in received_sounds_sorted_by_time[10:20]:
                heard_sounds = given_sound_objects_return_detected_sounds(
                    sound_objects=frame,
                    time_threshold_post_call=0.035,
                    angle_threshold=AZIMUTH,
                    dir_of_temporal_masking_fn_file=TEMPORAL_MASKING_DIR,
                    minimum_sound_detection_fraction=0.75,
                    focal_bat=FOCAL_BAT,
                    include_direct_sounds=INCLUDE_DIRECT_SOUNDS,
                )
                bat_call_time_for_given_interval = frame[1]["bat_last_call_time"]
                plt.axvspan(
                    bat_call_time_for_given_interval,
                    bat_call_time_for_given_interval + 0.005,
                    color=cm(FOCAL_BAT / NUM_COLORS),
                    ls="-.",
                )
                for sound_object in heard_sounds:

                    if (
                        sound_object["bat_direction"].angle_between(
                            sound_object["incident_direction"]
                        )
                        > AZIMUTH
                        or sound_object["bat_direction"].angle_between(
                            sound_object["incident_direction"]
                        )
                        < -AZIMUTH
                        or (
                            sound_object["type"] == "direct"
                            and sound_object["emitter_id"] == FOCAL_BAT
                        )
                    ):
                        continue

                    else:

                        if sound_object["type"] == "echo":
                            marker = "x"
                        else:
                            marker = "o"

                        if sound_object["emitter_id"] == FOCAL_BAT:
                            alpha = 1
                        else:
                            alpha = 0.5
                        if (
                            sound_object["time"] - sound_object["bat_last_call_time"]
                        ) < TIME_THRESHOLD:
                            time_axis = np.array(sound_object["occurance_times"])
                            intensity_axis = np.array(sound_object["all_spl_values"])
                            plt.scatter(
                                time_axis,
                                intensity_axis,
                                color=cm(sound_object["emitter_id"] / NUM_COLORS),
                                marker=marker,
                                alpha=alpha,
                            )

            plt.ylabel("SPL")
            plt.xlabel("time")
            plt.xlim(0.8, 2)
            dir_to_store = f"./dump_files/snr_{NUM_COLORS}_bats_with_directional_calls/intensity_vs_time_with_snr_direct_sounds_{INCLUDE_DIRECT_SOUNDS}/"
            make_dir(dir_to_store)
            plt.savefig(
                dir_to_store
                + f"bat_{FOCAL_BAT}_pm_{np.degrees(AZIMUTH):.2f}_time_threshold_after_call_{TIME_THRESHOLD}.png",
                transparent=True,
            )
            plt.clf()
