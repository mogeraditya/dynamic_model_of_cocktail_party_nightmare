# you have a list of sound objects
# first filtering is include direct sounds or not
import sys
from uuid import UUID

import numpy as np
import pandas as pd

sys.path.append("./dynamic_model")
import matplotlib.pyplot as plt
from read_simulation_output import read_data_per_simulation_per_bat
from supporting_files.utilities import make_dir

call_duration = 0.005
sim_time_step = 0.001
sim_rounding = 3


def parse_sound_info(
    sound_objects, time_threshold_post_call, focal_bat, include_direct_sounds
):
    # we look at some time interval after interpulse interval.
    # then we get sound intensity and if direct or echo for every unique sound id
    track_unique_ids = []
    store_serialized_sounds = []

    info_to_copy_from_sound = [
        "emitter_id",
        "bat_direction",
        "incident_direction",
        "type",
        "reflected_from",
        "sound_object_id",
        "bat_last_call_time",
    ]
    for sound in sound_objects:
        is_sound_direct_sound = sound["type"] == "direct"
        if not include_direct_sounds and is_sound_direct_sound:
            continue
        emission_time_post_call = sound["time"] - sound["bat_last_call_time"]
        sound_in_ipi = emission_time_post_call > call_duration
        sound_within_given_threshold = (
            emission_time_post_call < time_threshold_post_call
        )
        sound_is_self_call = (
            sound["emitter_id"] == focal_bat and sound["type"] == "direct"
        )
        if sound_in_ipi and sound_within_given_threshold and not sound_is_self_call:

            if sound["sound_object_id"] not in track_unique_ids:

                _temporary_dict = {}
                _temporary_dict["all_spl_values"] = []
                _temporary_dict["occurance_times"] = []
                _temporary_dict["ids"] = []

                track_unique_ids.append(sound["sound_object_id"])
                store_serialized_sounds.append(_temporary_dict)

                index_in_output_list = track_unique_ids.index(sound["sound_object_id"])

            elif sound["sound_object_id"] in track_unique_ids:
                index_in_output_list = track_unique_ids.index(sound["sound_object_id"])

            else:
                print(sound)
                raise ValueError

            store_serialized_sounds[index_in_output_list]["all_spl_values"].append(
                sound["received_spl"]
            )
            store_serialized_sounds[index_in_output_list]["occurance_times"].append(
                sound["time"]
            )
            store_serialized_sounds[index_in_output_list]["ids"].append(
                sound["sound_object_id"]
            )

            for key in info_to_copy_from_sound:
                store_serialized_sounds[index_in_output_list][key] = sound[key]

    for _dictionary in store_serialized_sounds:

        _dictionary["received_spl"] = np.round(
            np.mean(_dictionary["all_spl_values"]), sim_rounding
        )
        _dictionary["time"] = np.round(
            np.min(_dictionary["occurance_times"]), sim_rounding
        )
        _dictionary["duration"] = np.round(
            np.max(_dictionary["occurance_times"])
            - np.min(_dictionary["occurance_times"])
            + sim_time_step,
            sim_rounding,
        )
        # if len(_dictionary["occurance_times"]) > 5:
        #     print(_dictionary)
        #     raise
    return store_serialized_sounds


def find_sum_of_db(list_of_spls):
    _temporary_sum = 0
    for spl in list_of_spls:
        if spl != 0:
            _temporary_sum += 10 ** (spl / 20)
    if _temporary_sum == 0:
        return 0
    sum_of_spls_in_db = 20 * np.log10(_temporary_sum)
    return np.round(sum_of_spls_in_db, sim_rounding)


def generate_sound_profile(list_of_sounds, focal_sound_object):

    # the - - sim_time_step / 2 is cause numpy sometimes includes the last term wtf kms
    start_time_of_focal_sound = focal_sound_object["time"]
    ipi_start_time = focal_sound_object["bat_last_call_time"]

    duration_before_call_to_consider = (
        start_time_of_focal_sound - ipi_start_time + call_duration
    )
    start_of_time_axis = np.min([0.025, duration_before_call_to_consider])
    end_of_time_axis = -focal_sound_object["duration"] - 0.001

    time_axis_given_sound = np.round(
        np.arange(
            start_of_time_axis,
            end_of_time_axis - sim_time_step / 2,
            -sim_time_step,
        ),
        sim_rounding,
    )

    matrix_with_spls = np.zeros(shape=(len(time_axis_given_sound), len(list_of_sounds)))

    for i, sound in enumerate(list_of_sounds):
        if sound["sound_object_id"] != focal_sound_object["sound_object_id"]:
            time_of_sound_wrt_focal_sound = np.round(
                sound["time"] - focal_sound_object["time"], sim_rounding
            )

            time_intervals_to_add_intensity = np.arange(
                time_of_sound_wrt_focal_sound,
                time_of_sound_wrt_focal_sound + sound["duration"] - sim_time_step / 2,
                sim_time_step,
            )

            for j, time_step in enumerate(time_intervals_to_add_intensity):
                index_to_put_spl = np.where(time_axis_given_sound == time_step)[0]
                matrix_with_spls[index_to_put_spl, i] = sound["all_spl_values"][j]

    masker_profile = np.array([find_sum_of_db(i) for i in matrix_with_spls])
    echo_profile = (
        np.ones(shape=(len(time_axis_given_sound))) * focal_sound_object["received_spl"]
    )

    echo_masker_ratio = echo_profile - masker_profile
    return echo_masker_ratio, time_axis_given_sound


def get_temporal_masking_function_based_on_sound(
    time_axis_given_sound, dir_of_temporal_masking_fn_file, duration_of_sound
):
    temporal_masking_df = pd.read_csv(dir_of_temporal_masking_fn_file)
    output_thresholds = []
    for time_step in time_axis_given_sound:
        if time_step >= 0:
            subset_timegap_bin = time_step

        elif time_step < 0 and time_step >= -duration_of_sound:
            subset_timegap_bin = 0

        elif time_step < -duration_of_sound:
            subset_timegap_bin = time_step + duration_of_sound
        else:
            print(time_step)
            raise ValueError

        subset_of_temporal_masking_df = temporal_masking_df[
            (temporal_masking_df["timegap_ms"] >= subset_timegap_bin)
            & (temporal_masking_df["timegap_ms"] < subset_timegap_bin + sim_time_step)
        ]
        threshold_for_masking = np.mean(subset_of_temporal_masking_df["dB_leveldiff"])
        output_thresholds.append(threshold_for_masking)
    return output_thresholds


def is_signal_heard(
    sound,
    parsed_sounds,
    dir_of_temporal_masking_fn_file,
    minimum_echo_detection_fraction,
):
    echo_masker_ratio, time_axis_given_sound = generate_sound_profile(
        parsed_sounds, sound
    )
    temporal_masking_thresholds = get_temporal_masking_function_based_on_sound(
        time_axis_given_sound, dir_of_temporal_masking_fn_file, sound["duration"]
    )
    count_total = 0
    count_echo_greater_masking_threshold = 0

    for i, temporal_masking_threshold in enumerate(temporal_masking_thresholds):
        if echo_masker_ratio[i] >= temporal_masking_threshold:
            count_echo_greater_masking_threshold += 1
        count_total += 1

    percent_of_echo_detected = count_echo_greater_masking_threshold / count_total
    if percent_of_echo_detected >= minimum_echo_detection_fraction:
        return True
    elif percent_of_echo_detected < minimum_echo_detection_fraction:
        return False


def given_sound_objects_return_detected_sounds(
    sound_objects,
    time_threshold_post_call,
    dir_of_temporal_masking_fn_file,
    minimum_echo_detection_fraction,
    focal_bat,
    include_direct_sounds,
):
    parsed_sounds = parse_sound_info(
        sound_objects, time_threshold_post_call, focal_bat, include_direct_sounds
    )
    heard_sounds = []
    for sound in parsed_sounds:
        if is_signal_heard(
            sound,
            parsed_sounds,
            dir_of_temporal_masking_fn_file,
            minimum_echo_detection_fraction,
        ):
            heard_sounds.append(sound)

    return heard_sounds


if __name__ == "__main__":
    FOCAL_BAT = 0
    OUTPUT_DIR = f"./dump_files/snr_20_bats/{FOCAL_BAT}/"
    received_sounds_sorted_by_time = read_data_per_simulation_per_bat(
        OUTPUT_DIR, "received"
    )
    TEMPORAL_MASKING_DIR = "./exploratory_analysis/temporal_masking_fn.csv"
    # print(received_sounds_sorted_by_time[1])
    parsed_sounds = parse_sound_info(
        received_sounds_sorted_by_time[2],
        time_threshold_post_call=0.06,
        focal_bat=FOCAL_BAT,
        include_direct_sounds=True,
    )
    # print([i["received_spl"] for i in parsed_sounds])
    # print([i["duration"] for i in parsed_sounds])
    # print([i["sound_object_id"] for i in parsed_sounds])
    # print([i["emitter_id"] for i in parsed_sounds])
    # print([i["reflected_from"] for i in parsed_sounds])
    # print([i["type"] for i in parsed_sounds])
    # print([i["time"] for i in parsed_sounds])
    # print([i["bat_last_call_time"] for i in parsed_sounds])
    # print([[]] * 6)
    # received_sounds_sorted_by_time
    for sound in parsed_sounds:
        if sound["emitter_id"] == FOCAL_BAT:
            y = generate_sound_profile(parsed_sounds, sound)
            # plt.scatter(y[1], y[1], label="masker_profile", color="r")
            # plt.scatter(y[1], y[2], label="focal_sound_profile", color="b")
            plt.scatter(y[1], y[0], label="SNR", color="g")
            plt.scatter(
                y[1],
                get_temporal_masking_function_based_on_sound(
                    y[1], TEMPORAL_MASKING_DIR, sound["duration"]
                ),
                color="black",
            )
            plt.gca().invert_xaxis()
            plt.legend()
            plt.show()
    # heard_sounds = given_sound_objects_return_detected_sounds(
    #     sound_objects=received_sounds_sorted_by_time[1],
    #     time_threshold_post_call=0.06,
    #     dir_of_temporal_masking_fn_file=TEMPORAL_MASKING_DIR,
    #     minimum_echo_detection_fraction=0.25,
    # )
    # print(heard_sounds)
