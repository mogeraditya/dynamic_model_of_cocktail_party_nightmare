import sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.append("./dynamic_model")
from read_simulation_output import read_data_per_simulation_per_bat_received
from supporting_files.utilities import make_dir

# FOCAL_BAT = 0
NUM_COLORS = 10
AZIMUTHS = [np.pi / 6, np.pi / 3, np.pi / 2, np.pi]
for AZIMUTH in AZIMUTHS:
    for FOCAL_BAT in range(NUM_COLORS):
        OUTPUT_DIR = f"./simulation_outputs/10bats_selfecho_vs_other/{FOCAL_BAT}/"
        received_sounds_sorted_by_time = read_data_per_simulation_per_bat_received(
            OUTPUT_DIR
        )
        # print(received_sounds_sorted_by_time[0][-1])
        # print(received_sounds_sorted_by_time[1][0])
        # len(bats)
        cm = plt.get_cmap("gist_rainbow")
        # colors = plt.cm.tab10.colors
        plt.figure(figsize=(40, 10))
        for frame in received_sounds_sorted_by_time[0:20]:
            for sound_object in frame:
                if (
                    sound_object["spl"] == 100
                    and sound_object["emitter_id"] == FOCAL_BAT
                ):
                    plt.axvline(
                        sound_object["time"], color=cm(FOCAL_BAT / NUM_COLORS), ls="-."
                    )

                if (
                    sound_object["self_direction"].angle_between(
                        sound_object["incident_direction"]
                    )
                    > AZIMUTH
                    or sound_object["self_direction"].angle_between(
                        sound_object["incident_direction"]
                    )
                    < -AZIMUTH
                    or (
                        sound_object["type"] == "direct"
                        and sound_object["emitter_id"] == FOCAL_BAT
                    )
                ):
                    continue
                # print(sound_object)

                else:

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
                    plt.scatter(
                        sound_object["time"],
                        sound_object["spl"],
                        color=cm(sound_object["emitter_id"] / NUM_COLORS),
                        marker=marker,
                        alpha=alpha,
                    )

                # if (
                #     sound_object["time"] > 1.0
                #     and sound_object["time"] < 1.05
                #     and sound_object["emitter_id"] == 4
                #     and FOCAL_BAT == 0
                # ):
                #     print(sound_object)

        plt.ylabel("SPL")
        plt.xlabel("time")
        plt.xlim(1.0, 1.5)
        # plt.legend()
        dir_to_store = "./simulation_outputs/10bats_selfecho_vs_other/plots_self_echo_vs_other_sounds/"
        make_dir(dir_to_store)
        plt.savefig(dir_to_store + f"bat_{FOCAL_BAT}_pm_{np.degrees(AZIMUTH):.2f}.png")
        plt.clf()
