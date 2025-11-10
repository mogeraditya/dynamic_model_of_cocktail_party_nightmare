"""unit test to test bat objects"""

import math
import os
import sys
import unittest

import numpy as np

sys.path.append("./dynamic_model")
from agents.bats import Bat
from agents.sounds import DirectSound
from supporting_files.snr_implementation import *
from supporting_files.utilities import load_parameters
from supporting_files.vectors import Vector


class TestingSNR(unittest.TestCase):
    def setUp(self):
        sound1 = DirectSound(
            parameters_df=self.parameters_df,
            origin=self.sound_start_point,
            creation_time=self.creation_time,
            emitter_id=self.emitter_id,
            direction_vector=Vector(1, 0),
        )
