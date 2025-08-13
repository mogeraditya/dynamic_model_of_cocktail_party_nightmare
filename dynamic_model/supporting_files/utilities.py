"""These are misc functions that are used across many files"""

import os

import pandas


def make_dir(directory):
    """makes directory if the folder doesnt exist

    Args:
        directory (string): directory that needs to be made
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def convert_txt_to_int_or_float(txt):
    """convert a string to int if it can be made into an int.

    Args:
        txt (string): string to attempt conversion

    Returns:
        string/ int: is int if it can be converted else string
    """
    try:
        k = float(txt)
        if k % 1 == 0:
            return int(k)
        return k

    except ValueError:
        return txt


def load_parameters(file_dir):
    """load parameters from csv

    Args:
        file_dir (string): directory of the csv file

    Returns:
        DataFrame: DataFrame extracted from csv file
    """
    with open(file_dir, "r") as csv_file:
        reader = pandas.read_csv(csv_file)
    output_df = pandas.DataFrame()
    for key in reader.keys():
        value = reader[key][0]
        value = convert_txt_to_int_or_float(value)
        output_df[key] = [value]
    return output_df


# file_dir= r"../paramsets/mycsvfile.csv"
# df= load_parameters(file_dir)
# print(df)
# print(df["NUM_BATS"][0])
# print(type(df["NUM_BATS"][0]))
