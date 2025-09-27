import sys

import matplotlib.pyplot as plt
import numpy as np
from snr_implementation import given_sound_objects_return_detected_sounds

sys.path.append("./dynamic_model")
from read_simulation_output import read_data_per_simulation_per_bat
from supporting_files.utilities import make_dir

plt.style.use("dark_background")

FOCAL_BATS =  [1, 27, 35]
NUM_BATS = 50
TEMPORAL_MASKING_DIR = "./exploratory_analysis/temporal_masking_fn.csv"
INCLUDE_DIRECT_SOUNDS_ARR = [True]
AZIMUTH_THRESHOLDS = [np.pi / 6, np.pi / 2, np.pi]
DIR_SIMULATION_DATA = f"./dump_files/snr_{NUM_BATS}_bats"
APPLY_SNR = False

for INCLUDE_DIRECT_SOUNDS in INCLUDE_DIRECT_SOUNDS_ARR:
    for AZIMUTH in AZIMUTH_THRESHOLDS:
        for FOCAL_BAT in FOCAL_BATS:
            
            OUTPUT_DIR = DIR_SIMULATION_DATA + "/{FOCAL_BAT}/"
            received_sounds_sorted_by_time = read_data_per_simulation_per_bat(
                OUTPUT_DIR, "received"
            )

            cm = plt.get_cmap("gist_rainbow")

            interpulse_counter = 0
            for i, frame in enumerate(received_sounds_sorted_by_time[10:20]):
                if APPLY_SNR:
                    heard_sounds = given_sound_objects_return_detected_sounds(
                        sound_objects=frame,
                        time_threshold_post_call=0.035,
                        angle_threshold=AZIMUTH,
                        dir_of_temporal_masking_fn_file=TEMPORAL_MASKING_DIR,
                        minimum_sound_detection_fraction=0.75,
                        focal_bat=FOCAL_BAT,
                        include_direct_sounds=INCLUDE_DIRECT_SOUNDS,
                    )
                else:
                    heard_sounds = frame
                    
                fig, axs = plt.subplots(
                    1,
                    1,
                    figsize=(14, 14),
                    subplot_kw={"projection": "polar"},
                    layout="constrained",
                )

                axs.set_theta_zero_location("N")
                axs.set_theta_direction(-1)
                for sound_object in heard_sounds:

                    if sound_object["type"] == "echo":
                        marker = "x"
                    else:
                        marker = "o"

                    if sound_object["emitter_id"] == FOCAL_BAT:
                        color = cm(sound_object["emitter_id"] / NUM_BATS)
                        alpha = 1
                    else:
                        color = "grey"
                        alpha = 0.5

                    r = (
                        np.array(sound_object["occurance_times"])
                        - sound_object["bat_last_call_time"]
                    )
                    theta = [
                        sound_object["bat_direction"].angle_between(
                            sound_object["incident_direction"]
                        )
                    ] * len(r)

                    axs.scatter(
                        theta,
                        r,
                        color=color,
                        marker=marker,
                        alpha=alpha,
                    )
                dir_to_store = f"./dump_files/snr_{NUM_BATS}_bats/radial_snr_{APPLY_SNR}_direct_sounds_{INCLUDE_DIRECT_SOUNDS}_angle_threshold_{np.round(np.degrees(AZIMUTH),1)}/"
                make_dir(dir_to_store)
                plt.scatter(
                    0,
                    0,
                    color=cm(FOCAL_BAT / NUM_BATS),
                    label=f"focalbat={FOCAL_BAT}",
                )
                plt.ylim(0, 0.04)
                plt.legend()
                plt.savefig(
                    dir_to_store + f"bat_{FOCAL_BAT}_interpulse_number_{i+1}.png",
                    transparent=True,
                )
                print(f"done for bat_{FOCAL_BAT}_interpulse_number_{i+1}")
                plt.clf()
                interpulse_counter += 1
