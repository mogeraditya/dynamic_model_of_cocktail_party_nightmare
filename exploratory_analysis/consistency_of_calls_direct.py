# let us first think about a way to measure consistency
# so over time we track which echoes are heard first,  and if those echoes are coming back from the same source or not
# lets look at time series of echoes and the relative angle they come from

import sys

import matplotlib.pyplot as plt
import numpy as np
from snr_implementation import given_sound_objects_return_detected_sounds

sys.path.append("./dynamic_model")
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from read_simulation_output import read_data_per_simulation_per_bat
from snr_implementation import given_sound_objects_return_detected_sounds
from supporting_files.utilities import make_dir

sys.path.append("./dynamic_model")
from read_simulation_output import read_data_per_simulation_per_bat
from supporting_files.utilities import make_dir

plt.style.use("dark_background")

FOCAL_BATS = [1, 20]
NUM_COLORS = 50
TEMPORAL_MASKING_DIR = "./exploratory_analysis/temporal_masking_fn.csv"
DIRECTORY = f"/media/adityamoger/T7 Shield1/consistency_of_calls/DATA_effect_of_group_size/{NUM_COLORS}/iteration_number_3/"
DIRECTORY_STORE_PLOTS = "./exploratory_analysis/plots/"
INCLUDE_DIRECT_SOUNDS_ARR = [True]
AZIMUTH_THRESHOLDS = [np.pi / 6, np.pi / 2, np.pi]


for INCLUDE_DIRECT_SOUNDS in INCLUDE_DIRECT_SOUNDS_ARR:
    for FOCAL_BAT in FOCAL_BATS:
        for AZIMUTH in AZIMUTH_THRESHOLDS:

            track_unique_reflections = []
            sounds_to_plot = []
            times_of_sounds_to_plot = []
            delta_t = []
            OUTPUT_DIR = DIRECTORY + f"/{FOCAL_BAT}/"
            received_sounds_sorted_by_time = read_data_per_simulation_per_bat(
                OUTPUT_DIR, "received"
            )

            cm = plt.get_cmap("gist_rainbow")

            # interpulse_counter = 0
            # fig, axs = plt.subplots(
            #     1,
            #     1,
            #     figsize=(34, 14),
            #     # subplot_kw={"projection": "polar"},
            #     # layout="constrained",
            # )
            nan_matrix = (
                np.zeros(
                    shape=(len(received_sounds_sorted_by_time), NUM_COLORS - 1 + 4)
                )
                * np.nan
            )

            for i, frame in enumerate(received_sounds_sorted_by_time):
                heard_sounds = given_sound_objects_return_detected_sounds(
                    sound_objects=frame,
                    time_threshold_post_call=0.035,
                    angle_threshold=AZIMUTH,
                    dir_of_temporal_masking_fn_file=TEMPORAL_MASKING_DIR,
                    minimum_sound_detection_fraction=0.75,
                    focal_bat=FOCAL_BAT,
                    include_direct_sounds=INCLUDE_DIRECT_SOUNDS,
                )

                # plt.axvline(
                #     i * 0.04,
                #     color=cm(FOCAL_BAT / NUM_COLORS),
                #     # label=f"focalbat {FOCAL_BAT}, interpulse",
                # )

                for sound_object in heard_sounds:

                    time = (
                        np.array(sound_object["occurance_times"])[0]
                        - sound_object["bat_last_call_time"]
                        + i * 0.04
                    )
                    theta = sound_object["bat_direction"].angle_between(
                        sound_object["incident_direction"]
                    )

                    if sound_object["type"] == "echo":
                        marker = "x"
                    else:
                        marker = "o"

                    if sound_object["type"] == "direct":
                        # if sound_object["emitter_id"] == FOCAL_BAT:
                        reflected_from = f"bat_{sound_object["emitter_id"]}"

                        if reflected_from not in track_unique_reflections:
                            track_unique_reflections.append(reflected_from)
                            times_of_sounds_to_plot.append([])
                            sounds_to_plot.append([])
                            delta_t.append([])
                        index = track_unique_reflections.index(reflected_from)
                        sounds_to_plot[index].append(theta)
                        times_of_sounds_to_plot[index].append(time)
                        delta_t[index].append(
                            np.array(sound_object["occurance_times"])[0]
                            - sound_object["bat_last_call_time"]
                        )
                        # nan_matrix[i, index] = theta
                        nan_matrix[i, index] = (
                            np.array(sound_object["occurance_times"])[0]
                            - sound_object["bat_last_call_time"]
                        )
                    # else:
                    #     color = "grey"
                    #     alpha = 0.5
                    #     axs.scatter(
                    #         time,
                    #         theta,
                    #         color=color,
                    #         marker=marker,
                    #         alpha=alpha,
                    #     )

            # for j, sounds in enumerate(sounds_to_plot):
            #     axs.scatter(
            #         times_of_sounds_to_plot[j],
            #         sounds,
            #         label=f"reflected_from {track_unique_refelctions[j]}",
            #     )

            # dir_to_store = (
            #     DIRECTORY_STORE_PLOTS
            #     + f"/{FOCAL_BAT}/radial_with_snr_direct_sounds_{INCLUDE_DIRECT_SOUNDS}_angle_threshold_{np.round(np.degrees(AZIMUTH),1)}/"
            # )
            # make_dir(dir_to_store)

            # # plt.ylim(0, 0.04)
            # plt.xticks(
            #     ticks=np.arange(0.04, 0.04 * len(received_sounds_sorted_by_time), 0.04),
            #     labels=np.arange(1, len(received_sounds_sorted_by_time), 1),
            # )
            # plt.legend()
            # plt.show()
            # plt.savefig(
            #     dir_to_store + f"bat_{FOCAL_BAT}_interpulse_number_{i+1}.png",
            #     # transparent=True,
            # )

            # print(f"done for bat_{FOCAL_BAT}_interpulse_number_{i+1}")
            nan_matrix = nan_matrix[:, ~np.isnan(nan_matrix).all(0)]
            nan_matrix_rows = track_unique_reflections.copy()
            extender = [np.nan] * (NUM_COLORS - 1 + 4 - len(nan_matrix_rows))
            nan_matrix_rows.extend(extender)
            # fig, axs = plt.subplots(
            #     1,
            #     1,
            #     figsize=(34, 14),
            # )
            plt.figure(figsize=(40, 10))
            plt.imshow(nan_matrix.T, cmap=mpl.colormaps["viridis"])
            plt.colorbar(
                location="top",
                label="time delay post call",
            )
            plt.ylabel("direct call from")
            plt.xlabel("interpulse interval")
            print(nan_matrix.shape)
            print(len(nan_matrix_rows))
            # plt.yticks(labels=nan_matrix_rows, ticks=np.arange(0, nan_matrix.shape[1]))
            plt.yticks(
                labels=track_unique_reflections, ticks=np.arange(0, nan_matrix.shape[1])
            )
            plt.title(f"{NUM_COLORS} bats")
            # plt.clim(-np.pi, np.pi)
            plt.clim(0.005, 0.035)
            # plt.show()
            dir_to_store = DIRECTORY_STORE_PLOTS + f"/{NUM_COLORS}/{FOCAL_BAT}/"
            make_dir(dir_to_store)
            plt.savefig(
                dir_to_store
                + f"bat_{FOCAL_BAT}consistency_of_time_delay_othercalls_with_angle_threshold_{np.round(np.degrees(AZIMUTH),1)}.png",
                # transparent=True,
            )
            plt.clf()
            # interpulse_counter += 1
# print(delta_t)
# matrix_delta_t = np.matrix(delta_t)
