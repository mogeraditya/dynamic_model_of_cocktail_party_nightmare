# you have a list of sound objects
# first filtering is include direct sounds or not
import numpy as np
from supporting_files.utilities import change_tuples_to_vector_in_sound


def parse_sounds(
    sound_objects,
    time_threshold_post_call,
    angle_threshold,
    focal_bat,
    include_direct_sounds,
    call_duration,
):
    """Given a list of sound_objects, parse the sound objects.
    Parsing is done to ensure, sounds are within bats hearing field :math:`\\pm` angle_threshold
    and within the time threshold.

    Args:
        sound_objects (list): contains all the sound objects exracted from output files
        time_threshold_post_call (float): time interval after call for which the bat listens
        angle_threshold (float): :math:`\\pm` angle in radians of the bat's hearing field
        focal_bat (int): id of the bat that is hearing the sounds
        include_direct_sounds (bool): False if direct sounds shouldn't be considered
                                    in snr calculations.

    Returns:
        list: contains parsed sounds
    """

    parsed_sounds = []
    for sound in sound_objects:
        sound = change_tuples_to_vector_in_sound(sound)

        is_sound_direct_sound = sound["type"] == "direct"
        if not include_direct_sounds and is_sound_direct_sound:
            continue

        angle_of_sound_wrt_bat = sound["bat_direction"].angle_between(
            sound["incident_direction"]
        )
        sound_within_angle_threshold = (
            angle_of_sound_wrt_bat <= angle_threshold
            and angle_of_sound_wrt_bat >= -angle_threshold
        )

        emission_time_post_call = sound["time"] - sound["bat_last_call_time"]
        sound_in_ipi = emission_time_post_call > call_duration
        sound_within_time_threshold = emission_time_post_call < time_threshold_post_call
        sound_is_self_call = (
            sound["emitter_id"] == focal_bat and sound["type"] == "direct"
        )

        if (
            sound_in_ipi
            and sound_within_time_threshold
            and not sound_is_self_call
            and sound_within_angle_threshold
        ):
            parsed_sounds.append(sound)

    return parsed_sounds


def serialize_sound_info(parsed_sound_objects, sim_time_step, sim_rounding):
    """Sound objects are condensed to go from individual points
    at every timestep to one extended object.

    Args:
        parsed_sound_objects (list): contains all the parsed sounds

    Raises:
        ValueError: if sound id is not in list and in list then it raises an error

    Returns:
        list: contains parsed serialized sounds
    """
    # we look at some time interval after interpulse interval.
    # then we get sound intensity and if direct or echo for every unique sound id
    track_unique_ids = []
    store_serialized_sounds = []

    info_to_copy_from_sound = [
        "origin",
        "emitter_id",
        "bat_direction",
        "incident_direction",
        "type",
        "reflected_from",
        "sound_object_id",
        "bat_last_call_time",
        "sound_direction",
        "theta",
        "bat_position",
        "distance_from_bat",
        "creation_time",
    ]
    for sound in parsed_sound_objects:
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
            raise ValueError("Sound id is both inside and not inside list?!")

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

    return store_serialized_sounds


# @jit(nopython=False)
def find_sum_of_db(list_of_spls, sim_rounding):
    """Computes the sum of all the spls in a given list.

    Args:
        list_of_spls (list): contains all the spls (in dB scale) that need to be added

    Returns:
        float: sum of spls in the list (in dB scale)
    """
    _temporary_sum = 0
    for spl in list_of_spls:
        if spl != 0:
            _temporary_sum += 10 ** (spl / 20)
    if _temporary_sum == 0:
        return 0
    sum_of_spls_in_db = 20 * np.log10(_temporary_sum)
    return np.round(sum_of_spls_in_db, sim_rounding)


def sound_within_time_interval(sound, global_time_interval):
    is_sound_inside_time_interval = False
    if (
        sound["time"] >= global_time_interval[0]
        and sound["time"] < global_time_interval[1]
    ):
        is_sound_inside_time_interval = True
    return is_sound_inside_time_interval


def create_total_masking_profile(list_of_sounds, sim_time_step, sim_rounding):

    start_time_of_ipi = list_of_sounds[0]["bat_last_call_time"]
    end_time_of_ipi = np.max([i["time"] for i in list_of_sounds])
    time_axis_of_ipi = np.arange(
        start_time_of_ipi, end_time_of_ipi + sim_time_step / 2, sim_time_step
    )
    time_axis_of_ipi = np.round(time_axis_of_ipi, sim_rounding)
    matrix_to_store_spls = np.zeros(shape=(len(time_axis_of_ipi))).copy()

    for i, sound in enumerate(list_of_sounds):
        sound_detection_time = np.round(sound["time"], sim_rounding)
        index_to_put_spl = np.where(time_axis_of_ipi == sound_detection_time)[0]

        if matrix_to_store_spls[index_to_put_spl] == 0:
            matrix_to_store_spls[index_to_put_spl] = sound["received_spl"]
        else:
            matrix_to_store_spls[index_to_put_spl] = find_sum_of_db(
                [sound["received_spl"], matrix_to_store_spls[index_to_put_spl]],
                sim_rounding,
            )

    total_profile = matrix_to_store_spls
    return np.array(time_axis_of_ipi), total_profile


def filter_sounds_based_on_total_profile(list_of_sounds, sim_time_step, sim_rounding):
    filtered_list_of_sounds = []
    time_axis_of_ipi, total_profile = create_total_masking_profile(
        list_of_sounds, sim_time_step, sim_rounding
    )
    intensity_threshold_based_on_total_profile = total_profile - 34

    for sound in list_of_sounds:
        sound_detection_time = np.round(sound["time"], sim_rounding)
        index_based_on_time = np.where(time_axis_of_ipi == sound_detection_time)[0]

        sound_detection_intensity = sound["received_spl"]
        is_intensity_above_threshold = (
            sound_detection_intensity
            > intensity_threshold_based_on_total_profile[index_based_on_time]
        )

        if is_intensity_above_threshold:
            filtered_list_of_sounds.append(sound)

    return filtered_list_of_sounds


def given_focal_sound_find_time_axis_relevant_for_snr(
    focal_sound_object,
    time_extent_of_temporal_masking_fn_file,
    sim_time_step,
    sim_rounding,
):
    # the - sim_time_step / 2 is cause numpy sometimes includes the last term
    start_time_of_focal_sound = focal_sound_object["time"]
    ipi_start_time = focal_sound_object["bat_last_call_time"]
    duration_before_call_to_consider = start_time_of_focal_sound - ipi_start_time

    start_of_time_axis = np.min(
        [time_extent_of_temporal_masking_fn_file[0], duration_before_call_to_consider]
    )
    end_of_time_axis = (
        -focal_sound_object["duration"] + time_extent_of_temporal_masking_fn_file[1]
    )

    time_extent_of_masking_in_global_time = [
        start_time_of_focal_sound - start_of_time_axis,
        start_time_of_focal_sound - end_of_time_axis,
    ]

    time_axis_given_sound = np.round(
        np.arange(
            start_of_time_axis,
            end_of_time_axis - sim_time_step / 2,
            -sim_time_step,
        ),
        sim_rounding,
    )
    return time_extent_of_masking_in_global_time, time_axis_given_sound


def generate_sound_profile(
    list_of_sounds,
    focal_sound_object,
    time_extent_of_temporal_masking_fn_file,
    sim_time_step,
    sim_rounding,
):
    """given a focal sound and list of all sounds, generate focal_sound_to_masker_ratio
    computes both the focal_sound profile and masker sound profiles.


    Args:
        list_of_sounds (list): all sounds that can potentially mask the focal sound
        focal_sound_object (dict): focal sound
        time_extent_of_temporal_masking_fn_file (list): first entry is the time
        before a call to consider

    Returns:
        list,list: returns the focal sound to masker ratio and
        the time axis centered around focal sound
    """

    time_extent_of_masking_in_global_time, time_axis_given_sound = (
        given_focal_sound_find_time_axis_relevant_for_snr(
            focal_sound_object,
            time_extent_of_temporal_masking_fn_file,
            sim_time_step,
            sim_rounding,
        )
    )
    matrix_with_spls = np.zeros(shape=(len(time_axis_given_sound), len(list_of_sounds)))

    for i, sound in enumerate(list_of_sounds):
        is_sound_not_focal_sound = (
            sound["sound_object_id"] != focal_sound_object["sound_object_id"]
        )
        if is_sound_not_focal_sound and sound_within_time_interval(
            sound, time_extent_of_masking_in_global_time
        ):

            time_intervals_to_add_intensity = (
                sound["occurance_times"] - focal_sound_object["time"]
            )

            for j, time_step in enumerate(time_intervals_to_add_intensity):
                index_to_put_spl = np.where(time_axis_given_sound == time_step)[0]

                matrix_with_spls[index_to_put_spl, i] = sound["all_spl_values"][j]

    masker_profile = np.array(
        [find_sum_of_db(i, sim_rounding) for i in matrix_with_spls]
    )
    focal_sound_profile = (
        np.ones(shape=len(time_axis_given_sound)) * focal_sound_object["received_spl"]
    )

    focal_sound_masker_ratio = focal_sound_profile - masker_profile
    return focal_sound_masker_ratio, time_axis_given_sound


def get_temporal_masking_function_based_on_sound(
    time_axis_given_sound,
    temporal_masking_df,
    duration_of_sound,
    sim_time_step,
):
    """
    Args:
        time_axis_given_sound (list): time axis centered around focal sound
        dir_of_temporal_masking_fn_file (str): directory of temporal masking function file
        duration_of_sound (float): duration of the focal_sound

    Raises:
        ValueError: if time step is weird then raise error

    Returns:
        list: masking tolerance at each point on the time axis
    """
    masking_tolerance = []
    for time_step in time_axis_given_sound:
        if time_step >= 0:
            subset_timegap_bin = time_step

        elif time_step < 0 and time_step >= -duration_of_sound:
            subset_timegap_bin = 0

        elif time_step < -duration_of_sound:
            subset_timegap_bin = time_step + duration_of_sound
        else:
            raise ValueError

        timegaps = temporal_masking_df["timegap_ms"]
        mask = (subset_timegap_bin <= timegaps) & (
            timegaps < subset_timegap_bin + sim_time_step
        )
        subset_of_temporal_masking_df = {
            "timegap_ms": timegaps[mask],
            "dB_leveldiff": temporal_masking_df["dB_leveldiff"][mask],
        }

        threshold_for_masking = np.mean(subset_of_temporal_masking_df["dB_leveldiff"])
        masking_tolerance.append(threshold_for_masking)
    return masking_tolerance


def is_signal_heard(
    focal_sound,
    parsed_sounds,
    temporal_masking_df,
    minimum_sound_detection_fraction,
    sim_time_step,
    sim_rounding,
):
    """given sound and list of potentially masking sound, return if sound is heard or not
    if the sound to masker profile is atleast minimum_sound_detection_fraction
    then the sound is considered to be detected.

    Args:
        focal_sound (dict): focal sound
        parsed_sounds (list): list of all sounds that can potentially mask
        dir_of_temporal_masking_fn_file (str): directory of temporal masking function file
        minimum_sound_detection_fraction (float): fraction of sound to masker ratio
                                                that needs to be above masking tolerance
                                                for detection

    Returns:
        bool: true if sound is heard, else false
    """
    time_extent_of_temporal_masking_fn_file = [
        np.max(temporal_masking_df["timegap_ms"]),
        np.min(temporal_masking_df["timegap_ms"]),
    ]
    focal_sound_masker_ratio, time_axis_given_sound = generate_sound_profile(
        parsed_sounds,
        focal_sound,
        time_extent_of_temporal_masking_fn_file,
        sim_time_step,
        sim_rounding,
    )
    temporal_masking_thresholds = get_temporal_masking_function_based_on_sound(
        time_axis_given_sound,
        temporal_masking_df,
        focal_sound["duration"],
        sim_time_step,
    )
    count_total = 0
    count_focal_sound_greater_masking_threshold = 0

    for i, temporal_masking_threshold in enumerate(temporal_masking_thresholds):
        if focal_sound_masker_ratio[i] >= temporal_masking_threshold:
            count_focal_sound_greater_masking_threshold += 1
        count_total += 1

    percent_of_focal_sound_detected = (
        count_focal_sound_greater_masking_threshold / count_total
    )
    if percent_of_focal_sound_detected >= minimum_sound_detection_fraction:
        return True
    if percent_of_focal_sound_detected < minimum_sound_detection_fraction:
        return False
    else:
        raise ValueError("Percent focal sound is messed up!")


def given_sound_objects_return_detected_sounds(
    sound_objects,
    time_threshold_post_call,
    angle_threshold,
    temporal_masking_df,
    minimum_sound_detection_fraction,
    focal_bat,
    include_direct_sounds,
    call_duration,
    sim_time_step,
    sim_rounding,
):
    """given list of sounds, returns the list of sounds that are detected.
    if the sound to masker profile is atleast minimum_sound_detection_fraction
    then the sound is considered to be detected.

    Args:
        sound_objects (list): contains all the sound objects exracted from output files
        time_threshold_post_call (float): _description_
        angle_threshold (float): :math:`\\pm` angle in radians of the bat's hearing field
        dir_of_temporal_masking_fn_file (str): directory of temporal masking function file
        minimum_sound_detection_fraction (float): fraction of sound to masker ratio that
                                                needs to be above masking tolerance for detection
        focal_bat (int): id of the bat that is hearing the sounds
        include_direct_sounds (bool): False if direct sounds shouldn't be considered
                                    in snr calculations.

    Returns:
        list: contains heard sounds
    """

    parsed_sounds = parse_sounds(
        sound_objects,
        time_threshold_post_call,
        angle_threshold,
        focal_bat,
        include_direct_sounds,
        call_duration,
    )
    if len(parsed_sounds) == 0:
        return []
    parsed_serialized_sounds = filter_sounds_based_on_total_profile(
        parsed_sounds, sim_time_step, sim_rounding
    )
    parsed_serialized_sounds = serialize_sound_info(
        parsed_serialized_sounds, sim_time_step, sim_rounding
    )
    if len(parsed_serialized_sounds) == 0:
        return []

    heard_sounds = []
    for focal_sound in parsed_serialized_sounds:
        if is_signal_heard(
            focal_sound,
            parsed_serialized_sounds,
            temporal_masking_df,
            minimum_sound_detection_fraction,
            sim_time_step,
            sim_rounding,
        ):
            heard_sounds.append(focal_sound)

    return heard_sounds


# if __name__ == "__main__":
#     #     FOCAL_BAT = 0
#     #     OUTPUT_DIR = f"./dump_files/snr_20_bats/{FOCAL_BAT}/"
#     #     received_sounds_sorted_by_time = read_data_per_simulation_per_bat(
#     #         OUTPUT_DIR, "received"
#     #     )
#     TEMPORAL_MASKING_DIR = "./exploratory_analysis/temporal_masking_fn.csv"
#     # print(received_sounds_sorted_by_time[1])
#     parsed_sounds = parse_sound_info(
#         received_sounds_sorted_by_time[2],
#         time_threshold_post_call=0.06,
#         focal_bat=FOCAL_BAT,
#         include_direct_sounds=True,
#     )
#     # print([i["received_spl"] for i in parsed_sounds])
#     # print([i["duration"] for i in parsed_sounds])
#     # print([i["sound_object_id"] for i in parsed_sounds])
#     # print([i["emitter_id"] for i in parsed_sounds])
#     # print([i["reflected_from"] for i in parsed_sounds])
#     # print([i["type"] for i in parsed_sounds])
#     # print([i["time"] for i in parsed_sounds])
#     # print([i["bat_last_call_time"] for i in parsed_sounds])
#     # print([[]] * 6)
#     # received_sounds_sorted_by_time
#     for sound in parsed_sounds:
#         if sound["emitter_id"] == FOCAL_BAT:
#             y = generate_sound_profile(parsed_sounds, sound)
#             # plt.scatter(y[1], y[1], label="masker_profile", color="r")
#             # plt.scatter(y[1], y[2], label="focal_sound_profile", color="b")
#             plt.scatter(y[1], y[0], label="SNR", color="g")
#             plt.scatter(
#                 y[1],
#                 get_temporal_masking_function_based_on_sound(
#                     y[1], TEMPORAL_MASKING_DIR, sound["duration"]
#                 ),
#                 color="black",
#             )
#             plt.gca().invert_xaxis()
#             plt.legend()
#             plt.show()
#     # heard_sounds = given_sound_objects_return_detected_sounds(
#     #     sound_objects=received_sounds_sorted_by_time[1],
#     #     time_threshold_post_call=0.06,
#     #     dir_of_temporal_masking_fn_file=TEMPORAL_MASKING_DIR,
#     #     minimum_sound_detection_fraction=0.25,
#     # )
#     # print(heard_sounds)
# temporal_masking_df = pd.read_csv(TEMPORAL_MASKING_DIR)
# time_extent_of_temporal_masking_fn_file = [
#     np.max(temporal_masking_df["timegap_ms"]),
#     np.min(temporal_masking_df["timegap_ms"]),
# ]
# print(time_extent_of_temporal_masking_fn_file)
