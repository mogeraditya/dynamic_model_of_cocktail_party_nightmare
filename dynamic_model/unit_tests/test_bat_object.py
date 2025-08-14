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

print(os.getcwd())
DIR_PARAMS = "./dynamic_model/unit_tests/params_unittest/test_bat_object.csv"
OUTPUT_DIR = "./dynamic_model/unit_tests/detection_files/"


class TestingBatObject(unittest.TestCase):
    def setUp(self):
        self.origin = Vector(0, 0)
        self.creation_time = 0

        self.parameters_df = load_parameters(DIR_PARAMS)
        self.bat = Bat(self.parameters_df, output_dir=OUTPUT_DIR)

    def test_sound_detection(self):
        """Test the sound_detection"""
        # initialize the sound
        sound_disk_width = self.parameters_df["SOUND_DISK_WIDTH"][0]

        self.bat.position = self.origin
        sound1 = DirectSound(
            parameters_df=self.parameters_df,
            origin=Vector(-sound_disk_width, 0),
            creation_time=self.creation_time,
            emitter_id="sound1",
        )
        # sound2 = DirectSound(
        #     parameters_df=self.parameters_df,
        #     origin=Vector(-2 * sound_disk_width - 0.001, 0),
        #     creation_time=self.creation_time,
        #     emitter_id="sound2",
        # )
        # time_to_pass_one_meter = 1 / self.parameters_df["SOUND_SPEED"][0]  # seconds

        times_to_inspect = [
            0,
            0.0025,
            0.005,
            0.0075,
            0.01,
            0.0125,
            0.015,
            0.0175,
            0.0200,
        ]
        array_with_booleans = []
        for time_passed in times_to_inspect:
            sound1.update(time_passed)
            # sound2.update(time_passed)
            self.bat.detect_sounds(time_passed, [sound1])
            print(f"time passed= {time_passed:.4f}")

            if len(self.bat.received_sounds) > 0:
                array_with_booleans.append("detected")
            else:
                array_with_booleans.append("not detected")
            self.bat.received_sounds = []

        # _output_bool=
        expected_output = [
            "not detected",
            "not detected",
            "detected",
            "detected",
            "detected",
            "not detected",
            "not detected",
            "not detected",
            "not detected",
        ]

        self.assertTrue((array_with_booleans == expected_output))

    # def test_sound_disk_width(self):
    #     """check the width of the sound disk
    #     points that bound the sound and
    #     points in the middle and just outside
    #     are checked to see if they are correctly
    #     identified as lying outside the sound or not.
    #     """
    #     sound = DirectSound(
    #         parameters_df=self.parameters_df,
    #         origin=self.sound_start_point,
    #         creation_time=self.creation_time,
    #         emitter_id=self.emitter_id,
    #     )
    #     time_passed = 1  # seconds
    #     sound.update(time_passed)
    #     computed_width = [
    #         (time_passed - self.parameters_df["CALL_DURATION"][0])
    #         * self.parameters_df["SOUND_SPEED"][0],
    #         time_passed * self.parameters_df["SOUND_SPEED"][0],
    #     ]  # start and end of the sound disk
    #     points_to_check = [
    #         Vector(computed_width[0] - 0.001, 0),
    #         Vector(computed_width[0], 0),
    #         Vector(np.mean(computed_width), 0),
    #         Vector(computed_width[1], 0),
    #         Vector(computed_width[1] + 0.001, 0),
    #     ]
    #     store_boolean_per_point = []
    #     for point in points_to_check:
    #         _output = sound.contains_point(point)
    #         store_boolean_per_point.append(_output)

    #     self.assertTrue(store_boolean_per_point == [False, True, True, True, False])

    # def test_spl(self):
    #     """Test if spl calculation is accurate."""
    #     sound = DirectSound(
    #         parameters_df=self.parameters_df,
    #         origin=self.sound_start_point,
    #         creation_time=self.creation_time,
    #         emitter_id=self.emitter_id,
    #     )
    #     time_passed = 1
    #     radius = time_passed * self.parameters_df["SOUND_SPEED"][0]
    #     initial_spl = self.parameters_df["EMITTED_SPL"][0]
    #     distance_effect = 20 * math.log10(radius / 0.1)
    #     calculated_spl = (
    #         initial_spl
    #         - distance_effect
    #         - (self.parameters_df["AIR_ABSORPTION"][0] * radius)
    #     )

    #     sound.update(time_passed)
    #     object_spl = sound.current_spl

    #     self.assertEqual(object_spl, calculated_spl)


if __name__ == "__main__":

    unittest.main()
