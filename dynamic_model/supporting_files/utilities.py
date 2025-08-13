"""These are misc functions that are used across many files"""

import os

import numpy as np
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


def call_directionality_factor(A, theta):
    """Calculates the drop in source level as the angle
    increases from on-axis.

    The function calculates the drop using the third term
    in equation 11 of Giuggioli et al. 2015

     Parameters
    ----------
    A : float >0. Asymmetry parameter
    theta : float. Angle at which the call directionality factor is
            to be calculated in radians. 0 radians is on-axis.
      Returns
    -------

    call_dirn : float <=0. The amount of drop in dB which occurs when the call
                is measured off-axis.
    """
    if A <= 0:
        raise ValueError("A should be >0 ! ")

    call_dirn = A * (np.cos(theta) - 1)

    return call_dirn
