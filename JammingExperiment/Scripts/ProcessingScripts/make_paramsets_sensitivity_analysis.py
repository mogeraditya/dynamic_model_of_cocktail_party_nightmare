import csv
import math
import os
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.append("./dynamic_model")

from supporting_files.utilities import load_parameters, make_dir

simulation_parameters = load_parameters(
    r"./dynamic_model/paramsets/common_parameters.csv"
)

call_durations = [2,5,10]
call_rates = [[10,10], [10,20]]
emitted_spls = [80,100,120]
hearing_thresholds = [40,60,80]
bat_speeds = [1,3,5]
call_directionalities = [7,10]
hearing_directionalities = [2,7]
bat_rotation_speed = [180, 360, 540]
forward_masking_curve = 
