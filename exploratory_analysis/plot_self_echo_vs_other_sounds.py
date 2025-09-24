import sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.append("./dynamic_model")
from read_simulation_output import read_data_per_simulation_per_bat
from supporting_files.utilities import make_dir

# FOCAL_BAT = 0
NUM_COLORS = 50
AZIMUTHS = [np.pi / 6]
TIME_THRESHOLDS = [0.035]

for TIME_THRESHOLD in TIME_THRESHOLDS:
    for AZIMUTH in AZIMUTHS:
        for FOCAL_BAT in [1, 27, 35]:

            OUTPUT_DIR = f"./dump_files/snr_{NUM_COLORS}_bats/{FOCAL_BAT}/"
            received_sounds_sorted_by_time = read_data_per_simulation_per_bat(
                OUTPUT_DIR, "received"
            )
            # print(received_sounds_sorted_by_time[0][-1])
            # print(received_sounds_sorted_by_time[1][0])
            # len(bats)
            cm = plt.get_cmap("gist_rainbow")
            # colors = plt.cm.tab10.colors
            plt.figure(figsize=(60, 10))
            plt.style.use("dark_background")
            # print(received_sounds_sorted_by_time)
            for frame in received_sounds_sorted_by_time[10:20]:
                for sound_object in frame:
                    if (
                        sound_object["received_spl"] == 100
                        and sound_object["emitter_id"] == FOCAL_BAT
                    ):
                        plt.axvspan(
                            sound_object["time"],
                            sound_object["time"] + 0.005,
                            color=cm(FOCAL_BAT / NUM_COLORS),
                            ls="-.",
                        )

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
                            color = "green"
                            alpha = 1
                        else:
                            color = "red"
                            alpha = 0.5
                        if (
                            sound_object["time"] - sound_object["bat_last_call_time"]
                        ) < TIME_THRESHOLD:
                            plt.scatter(
                                sound_object["time"],
                                sound_object["received_spl"],
                                color=cm(sound_object["emitter_id"] / NUM_COLORS),
                                marker=marker,
                                alpha=alpha,
                            )

            plt.ylabel("SPL")
            plt.xlabel("time")
            plt.xlim(0.8, 2)
            # plt.legend()
            dir_to_store = "./dump_files/snr_{NUM_COLORS}_bats/intensity_vs_time/"
            make_dir(dir_to_store)
            plt.savefig(
                dir_to_store
                + f"bat_{FOCAL_BAT}_pm_{np.degrees(AZIMUTH):.2f}_time_threshold_after_call_{TIME_THRESHOLD}.png",
                transparent=True,
            )
            plt.clf()
