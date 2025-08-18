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
        sound_disk_width = self.parameters_df["SOUND_DISK_WIDTH"][0]

        self.bat.position = self.origin
        sound1 = DirectSound(
            parameters_df=self.parameters_df,
            origin=Vector(-sound_disk_width + 0.0001, 0),
            creation_time=self.creation_time,
            emitter_id="sound1",
        )
        sound2 = DirectSound(
            parameters_df=self.parameters_df,
            origin=Vector(-3 * sound_disk_width + 0.0001, 0),
            creation_time=self.creation_time,
            emitter_id="sound2",
        )

        times_to_inspect = np.arange(0, 0.025, 0.0025)
        array_with_booleans = []
        for time_passed in times_to_inspect:
            sound1.update(time_passed)
            sound2.update(time_passed)
            self.bat.detect_sounds(time_passed, [sound1, sound2])

            if len(self.bat.received_sounds) > 0:
                array_with_booleans.append("detected")
            else:
                array_with_booleans.append("not detected")
            # print(self.bat.received_sounds)
            # print(sound2)
            self.bat.received_sounds = []

        expected_output = [
            "not detected",
            "not detected",
            "detected",
            "detected",
            "not detected",
            "not detected",
            "detected",
            "detected",
            "not detected",
            "not detected",
        ]

        self.assertTrue((array_with_booleans == expected_output))

    def test_sound_emission(self):
        """check sound emission"""
        self.parameters_df["CALL_RATE"] = 1000
        self.bat = Bat(self.parameters_df, output_dir=OUTPUT_DIR)
        self.bat.time_since_last_call = 0.0
        self.bat.position = self.origin
        time_to_check = np.arange(0, 0.1, 0.01)
        sound_objects = []
        count_of_emitted_sounds = []
        for time in time_to_check:
            self.bat.update(time, sound_objects)
            count_of_emitted_sounds.append(len(sound_objects))
        expected_count_of_emitted_sounds = np.arange(1, 11, 1)
        self.assertTrue((count_of_emitted_sounds, expected_count_of_emitted_sounds))

    def test_movement(self):
        """check if movement is as expected."""
        self.parameters_df["PROPENSITY_TO_CHANGE_DIRECTION"] = 0
        self.bat = Bat(self.parameters_df, output_dir=OUTPUT_DIR)
        self.bat.position = self.origin
        self.bat.speed = 10.0  # m/s
        self.bat.direction = Vector(0, 1)
        self.bat.update_movement()
        expected_position = Vector(
            0, self.bat.speed * self.parameters_df["TIME_STEP"][0]
        )

        self.assertTrue(expected_position.compare(self.bat.position))


if __name__ == "__main__":

    unittest.main()
