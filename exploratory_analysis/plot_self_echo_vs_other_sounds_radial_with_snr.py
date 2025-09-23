import sys

import matplotlib.pyplot as plt
import numpy as np
from snr_implementation import given_sound_objects_return_detected_sounds

sys.path.append("./dynamic_model")
from read_simulation_output import read_data_per_simulation_per_bat
from supporting_files.utilities import make_dir

plt.style.use("dark_background")

FOCAL_BAT = 7
NUM_COLORS = 20
TEMPORAL_MASKING_DIR = "./exploratory_analysis/temporal_masking_fn.csv"
INCLUDE_DIRECT_SOUNDS = False

for FOCAL_BAT in [1, 7]:
    OUTPUT_DIR = f"./dump_files/snr_20_bats_2/{FOCAL_BAT}/"
    received_sounds_sorted_by_time = read_data_per_simulation_per_bat(
        OUTPUT_DIR, "received"
    )

    cm = plt.get_cmap("gist_rainbow")

    interpulse_counter = 0
    for i, frame in enumerate(received_sounds_sorted_by_time[1:10]):
        heard_sounds = given_sound_objects_return_detected_sounds(
            sound_objects=frame,
            time_threshold_post_call=0.035,
            dir_of_temporal_masking_fn_file=TEMPORAL_MASKING_DIR,
            minimum_echo_detection_fraction=0.75,
            focal_bat=FOCAL_BAT,
            include_direct_sounds=INCLUDE_DIRECT_SOUNDS,
        )
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
                alpha = 1
            else:
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
                color=cm(sound_object["emitter_id"] / NUM_COLORS),
                marker=marker,
                alpha=alpha,
            )
        dir_to_store = f"./dump_files/snr_20_bats_2/radial_with_snr_direct_sounds_{INCLUDE_DIRECT_SOUNDS}/"
        make_dir(dir_to_store)
        plt.ylim(0, 0.04)
        plt.savefig(
            dir_to_store + f"bat_{FOCAL_BAT}_interpulse_number_{i+1}.png",
            transparent=True,
        )
        print(f"done for bat_{FOCAL_BAT}_interpulse_number_{i+1}")
        plt.clf()
        interpulse_counter += 1
