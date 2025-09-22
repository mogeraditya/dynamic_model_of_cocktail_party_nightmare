# you have a list of sound objects
# first filtering is include direct sounds or not
import sys

import numpy as np

sys.path.append("./dynamic_model")
from read_simulation_output import read_data_per_simulation_per_bat
from supporting_files.utilities import make_dir


def parse_sound_info(sound_objects, time_threshold):
    # we look at some time interval after interpulse interval.
    # then we get sound intensity and if direct or echo for every unique sound id
    track_unique_ids = []

    _temporary_dict = {}
    _temporary_dict["all_spl_values"] = []
    _temporary_dict["occurance_times"] = []

    store_serialized_sounds = []
    generic_info_from_sound = ["emitter_id", "bat_direction", "incident_direction"]
    for sound in sound_objects:
        if (sound["time"] - sound["bat_last_call_time"]) > time_threshold:
            if sound["sound_object_id"] not in track_unique_ids:
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

    for _dictionary in store_serialized_sounds:
        _dictionary["received_spl"] = np.mean(_dictionary["all_spl_values"])
        _dictionary["time"] = np.min(_dictionary["occurance_times"])
        _dictionary["duration"] = np.max(_dictionary["occurance_times"]) - np.min(
            _dictionary["occurance_times"]
        )
        # _dictionary.pop("all_spl_values", None)
        # _dictionary.pop("occurance_times", None)

    return store_serialized_sounds


if __name__ == "__main__":
    FOCAL_BAT = 0
    OUTPUT_DIR = f"./dump_files/2bats_selfecho_vs_other/{FOCAL_BAT}/"
    received_sounds_sorted_by_time = read_data_per_simulation_per_bat(
        OUTPUT_DIR, "received"
    )
    # print(received_sounds_sorted_by_time[1])
    print(parse_sound_info(received_sounds_sorted_by_time[1], time_threshold=0.02))
