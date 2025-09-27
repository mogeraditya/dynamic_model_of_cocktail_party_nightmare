# let us first think about a way to measure consistency
# so over time we track which echoes are heard first,  and if those echoes are coming back from the same source or not
# lets look at time series of echoes and the relative angle they come from

import sys

import matplotlib.pyplot as plt
import numpy as np
from snr_implementation import given_sound_objects_return_detected_sounds

sys.path.append("./dynamic_model")
import sys

import matplotlib.pyplot as plt
import numpy as np
from read_simulation_output import read_data_per_simulation_per_bat
from snr_implementation import given_sound_objects_return_detected_sounds
from supporting_files.utilities import make_dir

sys.path.append("./dynamic_model")
from read_simulation_output import read_data_per_simulation_per_bat
from supporting_files.utilities import make_dir

plt.style.use("dark_background")

FOCAL_BATS = [1]
NUM_COLORS = 50
TEMPORAL_MASKING_DIR = "./exploratory_analysis/temporal_masking_fn.csv"
DIRECTORY = (
    f"./consistency_of_echoes/DATA_effect_of_group_size/{NUM_COLORS}/iteration_number_0"
)
DIRECTORY_STORE_PLOTS = "./exploratory_analysis/plots/"
INCLUDE_DIRECT_SOUNDS_ARR = [True]
AZIMUTH_THRESHOLDS = [np.pi / 6]

for INCLUDE_DIRECT_SOUNDS in INCLUDE_DIRECT_SOUNDS_ARR:
    for AZIMUTH in AZIMUTH_THRESHOLDS:
        for FOCAL_BAT in FOCAL_BATS:
            OUTPUT_DIR = DIRECTORY + f"/{FOCAL_BAT}/"
            received_sounds_sorted_by_time = read_data_per_simulation_per_bat(
                OUTPUT_DIR, "received"
            )

            cm = plt.get_cmap("gist_rainbow")

            interpulse_counter = 0
            fig, axs = plt.subplots(
                1,
                1,
                figsize=(34, 14),
                # subplot_kw={"projection": "polar"},
                # layout="constrained",
            )
            times = []
            angles = []
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
                time = frame[0]["bat_last_call_time"]
                times.append(time)
                # plt.axvline(
                #     frame[0]["bat_last_call_time"],
                #     color=cm(FOCAL_BAT / NUM_COLORS),
                #     # label=f"focalbat {FOCAL_BAT}, interpulse",
                # )

                # axs.set_theta_zero_location("N")
                # axs.set_theta_direction(-1)
                angles_for_one_ipi = []
                for sound_object in heard_sounds:

                    time = sound_object["occurance_times"][0]

                    if sound_object["emitter_id"] == FOCAL_BAT:
                        theta = sound_object["bat_direction"].angle_between(
                            sound_object["incident_direction"]
                        )
                        angles_for_one_ipi.append(theta)

                plt.plot([time] * len(angles_for_one_ipi), angles_for_one_ipi)
                angles.append(angles_for_one_ipi)

            plt.show()
            # dir_to_store = (
            #     DIRECTORY_STORE_PLOTS
            #     + f"/{FOCAL_BAT}/radial_with_snr_direct_sounds_{INCLUDE_DIRECT_SOUNDS}_angle_threshold_{np.round(np.degrees(AZIMUTH),1)}/"
            # )
            # make_dir(dir_to_store)

            # # plt.ylim(0, 0.04)
            # plt.legend()
            # plt.savefig(
            #     dir_to_store + f"bat_{FOCAL_BAT}_interpulse_number_{i+1}.png",
            #     # transparent=True,
            # )

            # print(f"done for bat_{FOCAL_BAT}_interpulse_number_{i+1}")
            # plt.clf()
            # interpulse_counter += 1
