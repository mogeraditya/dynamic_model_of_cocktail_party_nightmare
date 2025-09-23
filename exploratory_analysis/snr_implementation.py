# you have a list of sound objects
# first filtering is include direct sounds or not
import sys

import numpy as np
import pandas as pd

sys.path.append("./dynamic_model")
import matplotlib.pyplot as plt
from read_simulation_output import read_data_per_simulation_per_bat
from supporting_files.utilities import make_dir

call_duration = 0.005
sim_time_step = 0.001
sim_rounding = 3


def parse_sound_info(sound_objects, time_threshold_post_call):
    # we look at some time interval after interpulse interval.
    # then we get sound intensity and if direct or echo for every unique sound id
    track_unique_ids = []

    store_serialized_sounds = []
    generic_info_from_sound = [
        "emitter_id",
        "bat_direction",
        "incident_direction",
        "type",
        "reflected_from",
        "sound_object_id",
        "bat_last_call_time",
    ]
    for sound in sound_objects:
        if (
            sound["time"] - sound["bat_last_call_time"]
        ) < time_threshold_post_call and (
            sound["time"] - sound["bat_last_call_time"]
        ) > call_duration:
            if sound["sound_object_id"] not in track_unique_ids:
                _temporary_dict = {}
                _temporary_dict["all_spl_values"] = []
                _temporary_dict["occurance_times"] = []
                track_unique_ids.append(sound["sound_object_id"])
                store_serialized_sounds.append(_temporary_dict)

                index_in_output_list = track_unique_ids.index(sound["sound_object_id"])

            else:
                index_in_output_list = track_unique_ids.index(sound["sound_object_id"])

            store_serialized_sounds[index_in_output_list]["all_spl_values"].append(
                sound["received_spl"]
            )
            store_serialized_sounds[index_in_output_list]["occurance_times"].append(
                sound["time"]
            )

            for key in generic_info_from_sound:
                store_serialized_sounds[index_in_output_list][key] = sound[key]
    # print(store_serialized_sounds)
    # print(sound_objects[2]["sound_object_id"])
    # print([i for i in track_unique_ids])
    # print([i["sound_object_id"] for i in store_serialized_sounds])
    # print(track_unique_ids.index(sound_objects[2]["sound_object_id"]))

    for _dictionary in store_serialized_sounds:
        # print(_dictionary)
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
        # _dictionary.pop("all_spl_values", None)
        # _dictionary.pop("occurance_times", None)
    # print(track_unique_ids)
    return store_serialized_sounds


def find_sum_of_db(list_of_spls):
    _temporary_sum = 0
    for spl in list_of_spls:
        if spl != 0:
            _temporary_sum += 10 ** (spl / 10)
    if _temporary_sum == 0:
        return 0
    sum_of_spls_in_db = 10 * np.log10(_temporary_sum)
    return np.round(sum_of_spls_in_db, sim_rounding)


def generate_profile(list_of_sounds, focal_sound_object):

    # the - - sim_time_step / 2 is cause numpy sometimes includes the last term wtf kms
    start_time_of_focal_sound = focal_sound_object["time"]
    ipi_start_time = focal_sound_object["bat_last_call_time"]
    duration_before_call_to_consider = (
        start_time_of_focal_sound - ipi_start_time + call_duration
    )
    time_axis_given_sound = np.round(
        np.arange(
            duration_before_call_to_consider,
            -focal_sound_object["duration"] - 0.001 - sim_time_step / 2,
            -sim_time_step,
        ),
        sim_rounding,
    )
    matrix_store_spl = np.zeros(shape=(len(time_axis_given_sound), len(list_of_sounds)))

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
            # print(time_intervals_to_add_intensity)
            # print(sound["all_spl_values"])
            # print(sound["occurance_times"] - start_time_of_focal_sound)
            # print(sound)
            for j, time_step in enumerate(time_intervals_to_add_intensity):
                index_to_put_spl = np.where(time_axis_given_sound == time_step)[0]
                print(sound["all_spl_values"])
                print(time_intervals_to_add_intensity)
                print(sound["duration"])
                matrix_store_spl[index_to_put_spl, i] = sound["all_spl_values"][j]

    masker_profile = np.array([find_sum_of_db(i) for i in matrix_store_spl])
    echo_profile = (
        np.ones(shape=(len(time_axis_given_sound))) * focal_sound_object["received_spl"]
    )

    # time_intervals_to_add_intensity = np.arange(
    #     0.0,
    #     0.0 - focal_sound_object["duration"] + sim_time_step / 2,
    #     -sim_time_step,
    # )
    # # print(time_intervals_to_add_intensity)
    # # print(focal_sound_object["all_spl_values"])
    # for i, time_step in enumerate(time_intervals_to_add_intensity):
    #     index_to_put_spl = np.where(time_axis_given_sound == time_step)[0]
    #     echo_profile[index_to_put_spl] = focal_sound_object["all_spl_values"][i]

    # print(masker_profile)
    # print(echo_profile)
    echo_masker_ratio = echo_profile - masker_profile
    return echo_masker_ratio, time_axis_given_sound


# def is_signal_detected (serialized_sound_objects, focal_sound_object_id):
#     masking_sounds = []
#     for sound in serialized_sound_objects:
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
    echo_masker_ratio, time_axis_given_sound = generate_profile(parsed_sounds, sound)
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
    else:
        return False


def given_sound_objects_return_detected_sounds(
    sound_objects,
    time_threshold_post_call,
    dir_of_temporal_masking_fn_file,
    minimum_echo_detection_fraction,
):
    parsed_sounds = parse_sound_info(sound_objects, time_threshold_post_call)
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
    # parsed_sounds = parse_sound_info(
    #     received_sounds_sorted_by_time[1], time_threshold_post_call=0.06
    # )
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
    # for sound in parsed_sounds:
    #     if sound["emitter_id"] == FOCAL_BAT:
    #         y = generate_profile(parsed_sounds, sound)
    #         plt.scatter(y[3], y[1], label="masker_profile", color="r")
    #         plt.scatter(y[3], y[2], label="focal_sound_profile", color="b")
    #         plt.scatter(y[3], y[0], label="SNR", color="g")
    #         plt.plot(
    #             y[3],
    #             get_temporal_masking_function_based_on_sound(
    #                 y[3], TEMPORAL_MASKING_DIR, sound["duration"]
    #             ),
    #             color="black",
    #         )
    #         plt.gca().invert_xaxis()
    #         plt.legend()
    #         plt.show()
    heard_sounds = given_sound_objects_return_detected_sounds(
        sound_objects=received_sounds_sorted_by_time[1],
        time_threshold_post_call=0.06,
        dir_of_temporal_masking_fn_file=TEMPORAL_MASKING_DIR,
        minimum_echo_detection_fraction=0.25,
    )
    print(heard_sounds)
