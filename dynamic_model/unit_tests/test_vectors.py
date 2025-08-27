"""unit test to test sound propagation"""

import math
import os
import sys
import unittest

import numpy as np

sys.path.append("./dynamic_model")
from agents.bats import Bat
from agents.sounds import DirectSound
from supporting_files.utilities import load_parameters
from supporting_files.vectors import Vector

# sys.path.insert(1, ".")
Bat._id_counter = 0
print(os.getcwd())
DIR_PARAMS = "./dynamic_model/unit_tests/params_unittest/test_bat_object.csv"
OUTPUT_DIR = "./dynamic_model/unit_tests/detection_files/"


class TestingBatObject(unittest.TestCase):
    def setUp(self):
        self.vector = Vector(0, 1)

    def test_angle(self):
        vector_at_plus90 = Vector(-1, 0)
        vector_at_minus90 = Vector(1, 0)
        print(np.degrees(self.vector.angle_between((vector_at_plus90))))
        print(self.vector.angle_between((vector_at_minus90)))
        print(vector_at_minus90 == vector_at_minus90)
        print(vector_at_minus90.rotate(-np.pi / 2))
        print(np.random.normal(0, 0.02, 10))


if __name__ == "__main__":

    unittest.main()
