"""unit test to test sound propagation"""

import math
import os
import sys
import unittest

import numpy as np

sys.path.append("./dynamic_model")
from agents.sounds import DirectSound
from supporting_files.utilities import load_parameters
from supporting_files.vectors import Vector

# sys.path.insert(1, ".")

print(os.getcwd())
DIR_PARAMS = "./dynamic_model/unit_tests/params_unittest/test_sound_propagation.csv"


class TestingSoundPropagation(unittest.TestCase):
    def setUp(self):
        self.sound_start_point = Vector(0, 0)
        self.creation_time = 0
        self.emitter_id = "tester"
        self.parameters_df = load_parameters(DIR_PARAMS)

    def test_radius_after_time(self):
        """Test the radius increase with time."""
        # initialize the sound
        sound = DirectSound(
            parameters_df=self.parameters_df,
            origin=self.sound_start_point,
            creation_time=self.creation_time,
            emitter_id=self.emitter_id,
        )
        time_passed = 5  # seconds
        sound.update(time_passed)
        calculated_radius = time_passed * self.parameters_df["SOUND_SPEED"][0]
        radius_of_sound_after_update = sound.current_radius
        self.assertTrue((radius_of_sound_after_update == calculated_radius))

    def test_sound_disk_width(self):
        """check the width of the sound disk
        points that bound the sound and
        points in the middle and just outside
        are checked to see if they are correctly
        identified as lying outside the sound or not.
        """
        sound = DirectSound(
            parameters_df=self.parameters_df,
            origin=self.sound_start_point,
            creation_time=self.creation_time,
            emitter_id=self.emitter_id,
        )
        time_passed = 1  # seconds
        sound.update(time_passed)
        computed_width = [
            (time_passed - self.parameters_df["CALL_DURATION"][0])
            * self.parameters_df["SOUND_SPEED"][0],
            time_passed * self.parameters_df["SOUND_SPEED"][0],
        ]  # start and end of the sound disk
        points_to_check = [
            Vector(computed_width[0] - 0.001, 0),
            Vector(computed_width[0], 0),
            Vector(np.mean(computed_width), 0),
            Vector(computed_width[1], 0),
            Vector(computed_width[1] + 0.001, 0),
        ]
        store_boolean_per_point = []
        for point in points_to_check:
            _output = sound.contains_point(point)
            store_boolean_per_point.append(_output)

        self.assertTrue(store_boolean_per_point == [False, True, True, True, False])

    def test_spl(self):
        """Test if spl calculation is accurate."""
        sound = DirectSound(
            parameters_df=self.parameters_df,
            origin=self.sound_start_point,
            creation_time=self.creation_time,
            emitter_id=self.emitter_id,
        )
        time_passed = 1
        radius = time_passed * self.parameters_df["SOUND_SPEED"][0]
        initial_spl = self.parameters_df["EMITTED_SPL"][0]
        distance_effect = 20 * math.log10(radius / 1)
        calculated_spl = (
            initial_spl
            - distance_effect
            - (self.parameters_df["AIR_ABSORPTION"][0] * radius)
        )

        sound.update(time_passed)
        object_spl = sound.current_spl

        self.assertEqual(object_spl, calculated_spl)


if __name__ == "__main__":

    unittest.main()
