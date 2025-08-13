"""Parse all the folders in storage area for received and emitted data"""

import glob

import numpy as np
from supporting_files.utilities import convert_txt_to_int_or_float


def read_data_per_simulation(output_dir):
    """read data that is saved by one isntance of simulation

    Args:
        output_dir (string): directory of the stored files

    Returns:
        list: dictionaries consisting of emitted and received sounds by all the bats in a simulation.
    """
    list_of_bats_in_simulation = glob.glob(output_dir + "*")

    list_of_bats_in_simulation = [
        convert_txt_to_int_or_float(i[-1]) for i in list_of_bats_in_simulation
    ]

    list_of_bats_in_simulation = [
        i for i in list_of_bats_in_simulation if isinstance(i, int)
    ]

    list_of_folders_per_bat = glob.glob(output_dir + "*")
    list_of_folders_per_bat = [
        i
        for i in list_of_folders_per_bat
        if isinstance(convert_txt_to_int_or_float(i[-1]), int)
    ]

    dict_to_store_all_data_received = {}
    dict_to_store_all_data_emitted = {}
    for i, folder_dir_per_bat in enumerate(list_of_folders_per_bat):
        # print(folder_dir_per_bat)
        _array_to_dump_data_received = read_data_per_simulation_per_bat_received(
            folder_dir_per_bat
        )

        dict_to_store_all_data_received[list_of_bats_in_simulation[i]] = (
            _array_to_dump_data_received
        )

        _array_to_dump_data_emitted = read_data_per_simulation_per_bat_emitted(
            folder_dir_per_bat
        )
        dict_to_store_all_data_emitted[list_of_bats_in_simulation[i]] = (
            _array_to_dump_data_emitted
        )

    return dict_to_store_all_data_emitted, dict_to_store_all_data_received


def read_data_per_simulation_per_bat_received(folder_dir):
    """reads the files containing received sounds per bat

    Args:
        folder_dir (string): directory per bat where received sounds are saved

    Returns:
        list: array containing all the received data per bat
    """
    list_of_files_per_bat = glob.glob(folder_dir + "/*_received_*.npy")
    _array_to_dump_data = []
    for file_dir in list_of_files_per_bat:
        data_per_timestep = np.load(file_dir, allow_pickle=True)
        _array_to_dump_data.append(data_per_timestep)
    return _array_to_dump_data


def read_data_per_simulation_per_bat_emitted(folder_dir):
    """reads the files containing emitted sounds per bat

    Args:
        folder_dir (string): directory per bat where emitted sounds are saved

    Returns:
        list: array containing all the emitted data per bat
    """
    list_of_files_per_bat = glob.glob(folder_dir + "/*_emitted_*.npy")
    _array_to_dump_data = []
    for file_dir in list_of_files_per_bat:
        data_per_timestep = np.load(file_dir, allow_pickle=True)
        _array_to_dump_data.append(data_per_timestep)
    return _array_to_dump_data


dict_1, dict_2 = read_data_per_simulation(
    r"/home/adityamoger/Documents/GitHub/dynamic_model_of_cocktail_party_nightmare/test_storage/"
)

# dir = r"/home/adityamoger/Documents/GitHub/dynamic_model_of_cocktail_party_nightmare/test_storage_multiple_echoes/*"
# print(glob.glob(dir))
