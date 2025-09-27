import sys

import matplotlib.pyplot as plt
import numpy as np
from snr_implementation import given_sound_objects_return_detected_sounds

sys.path.append("./dynamic_model")
from read_simulation_output import read_data_per_simulation_per_bat
from supporting_files.utilities import make_dir

plt.style.use("dark_background")

FOCAL_BATS = [1]
NUM_BATS = 50
TEMPORAL_MASKING_DIR = "./exploratory_analysis/temporal_masking_fn.csv"
DIRECTORY = (
    f"./consistency_of_echoes/DATA_effect_of_group_size/{NUM_BATS}/iteration_number_0"
)
DIRECTORY_STORE_PLOTS = "./exploratory_analysis/plots/"
INCLUDE_DIRECT_SOUNDS_ARR = [True]
AZIMUTH_THRESHOLDS = [np.pi / 2]
CM = plt.get_cmap("gist_rainbow")

for INCLUDE_DIRECT_SOUNDS in INCLUDE_DIRECT_SOUNDS_ARR:
    for AZIMUTH in AZIMUTH_THRESHOLDS:
        for FOCAL_BAT in FOCAL_BATS:
            OUTPUT_DIR = DIRECTORY + f"/{FOCAL_BAT}/"
            received_sounds_sorted_by_time = read_data_per_simulation_per_bat(
                OUTPUT_DIR, "received"
            )
            NUM_COLORS = len(received_sounds_sorted_by_time)

            times_delays = []

            fig, axs = plt.subplots(
                1,
                1,
                figsize=(14, 14),
                subplot_kw={"projection": "polar"},
                layout="constrained",
            )
            axs.set_theta_zero_location("N")
            axs.set_theta_direction(-1)

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
                #     frame[0]["bat_last_call_time"],
                #     color=cm(FOCAL_BAT / NUM_COLORS),
                #     # label=f"focalbat {FOCAL_BAT}, interpulse",
                # )

                # axs.set_theta_zero_location("N")
                # axs.set_theta_direction(-1)
                angles_for_one_ipi = []
                sounds_to_consider, intensities = [], []
                for sound_object in heard_sounds:

                    time = sound_object["occurance_times"][0]

                    if sound_object["emitter_id"] == FOCAL_BAT:
                        sounds_to_consider.append(sound_object)
                        intensities.append(sound_object["received_spl"])

                if len(sounds_to_consider) != 0:
                    focal_sound = sounds_to_consider[np.argmax(intensities)]
                    r = (
                        np.array(focal_sound["occurance_times"])
                        - focal_sound["bat_last_call_time"]
                    )
                    theta = [
                        focal_sound["bat_direction"].angle_between(
                            focal_sound["incident_direction"]
                        )
                    ] * len(r)
                    axs.plot(
                        theta,
                        r,
                        color=CM(i / NUM_COLORS),
                        label=f"interpulse_number_{i}_reflected_from_{focal_sound["reflected_from"]}",
                    )

                # angles.append(angles_for_one_ipi)
            axs.set_thetamin(-np.degrees(AZIMUTH))
            axs.set_thetamax(np.degrees(AZIMUTH))
            plt.legend()
            plt.show()
