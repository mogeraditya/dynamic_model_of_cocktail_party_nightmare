import sys

import matplotlib.pyplot as plt
import numpy as np
from snr_implementation import given_sound_objects_return_detected_sounds

sys.path.append("./dynamic_model")
from read_simulation_output import read_data_per_simulation_per_bat
from supporting_files.utilities import make_dir

plt.style.use("dark_background")

FOCAL_BAT = 7
NUM_COLORS = 10
TEMPORAL_MASKING_DIR = "./exploratory_analysis/temporal_masking_fn.csv"

for FOCAL_BAT in [0, 7, 17]:
    OUTPUT_DIR = f"./dump_files/snr_10_bats/{FOCAL_BAT}/"
    received_sounds_sorted_by_time = read_data_per_simulation_per_bat(
        OUTPUT_DIR, "received"
    )
    # print(received_sounds_sorted_by_time[0][-1])
    # print(received_sounds_sorted_by_time[1][0])
    # len(bats)
    cm = plt.get_cmap("gist_rainbow")
    # colors = plt.cm.tab10.colors
    interpulse_counter = 0
    for i, frame in enumerate(received_sounds_sorted_by_time[1:10]):
        heard_sounds = given_sound_objects_return_detected_sounds(
            sound_objects=frame,
            time_threshold_post_call=np.inf,
            dir_of_temporal_masking_fn_file=TEMPORAL_MASKING_DIR,
            minimum_echo_detection_fraction=0.25,
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
            # section to rebuild vector objects

            if (
                sound_object["received_spl"] == 100
                and sound_object["emitter_id"] == FOCAL_BAT
            ):
                # plt.axvline(
                #     sound_object["time"], color=cm(FOCAL_BAT / NUM_COLORS), ls="-."
                # )
                print(sound_object["time"])
                value = sound_object["time"]
            # else:

            # fig, axs = plt.subplots(
            #     1,
            #     1,
            #     figsize=(5, 8),
            #     subplot_kw={"projection": "polar"},
            #     layout="constrained",
            # )

            # if sound_object["type"] == "echo":
            #     marker = "x"
            # else:
            #     marker = "o"

            # if sound_object["emitter_id"] == FOCAL_BAT:
            #     color = "green"
            #     alpha = 1
            # else:
            #     color = "red"
            #     alpha = 0.5

            # axs.scatter(

            #     sound_object["incident_direction"],
            #     sound_object["time"]
            #     color=cm(sound_object["emitter_id"] / NUM_COLORS),
            #     marker=marker,
            #     alpha=alpha,
            # )
            # if sound_object["time"] > 0.27 and sound_object["time"] < 0.320:

            if sound_object["type"] == "echo":
                marker = "x"
            else:
                marker = "o"

            if sound_object["emitter_id"] == FOCAL_BAT:
                color = "green"
                alpha = 1
            else:
                color = "red"
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
        dir_to_store = "./dump_files/snr_10_bats/plots_self_echo_vs_other_sounds_radial_transparent_with_snr/"
        make_dir(dir_to_store)
        plt.ylim(0, 0.1)
        plt.savefig(
            dir_to_store + f"bat_{FOCAL_BAT}_interpulse_number_{i+1}.png",
            transparent=True,
        )
        print(f"done for bat_{FOCAL_BAT}_interpulse_number_{i+1}")
        plt.clf()
        interpulse_counter += 1
# plt.show()
# plt.ylabel("SPL")
# plt.xlabel("time")
# plt.xlim(1.0, 1.5)
# # plt.legend()
# dir_to_store = "./simulation_outputs/10bats_selfecho_vs_other/plots_self_echo_vs_other_sounds/"
# make_dir(dir_to_store)
# plt.savefig(dir_to_store + f"bat_{FOCAL_BAT}_pm_{np.degrees(AZIMUTH):.2f}.png")
# plt.clf()
