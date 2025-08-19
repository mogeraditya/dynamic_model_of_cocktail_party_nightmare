"""unit test to test sound propagation"""

import sys
import unittest

import numpy as np

sys.path.append("./dynamic_model")
from agents.bats import Bat
from agents.sounds import DirectSound
from simulation import Simulation
from supporting_files.utilities import load_parameters
from supporting_files.vectors import Vector

# sys.path.insert(1, ".")


DIR_PARAMS = (
    "./dynamic_model/unit_tests/params_unittest/test_reflections_in_simulation.csv"
)
OUTPUT_DIR = "./dynamic_model/unit_tests/simulation_test_files/"


class TestReflections(unittest.TestCase):
    def setUp(self):
        self.origin = Vector(0, 0)
        self.creation_time = 0

        self.parameters_df = load_parameters(DIR_PARAMS)
        self.bat = Bat(self.parameters_df, output_dir=OUTPUT_DIR)
        self.simulation = Simulation(DIR_PARAMS, OUTPUT_DIR)

    def test_echo_generation(self):
        """Test the echo generation"""
        sound_disk_width = self.parameters_df["SOUND_DISK_WIDTH"][0]
        self.bat.speed = 0
        self.bat.position = Vector(0, 0)
        self.simulation.bats = [self.bat]
        time_passed = 0.005
        sound1 = DirectSound(
            parameters_df=self.parameters_df,
            origin=Vector(-sound_disk_width, 0),
            creation_time=self.creation_time,
            emitter_id="sound1",
        )
        times_to_inspect = np.arange(0, 0.015, 0.0025)
        array_with_booleans = []
        self.simulation.sound_objects = [sound1]
        for i, time_passed in enumerate(times_to_inspect):
            for sound in self.simulation.sound_objects:
                sound.update(time_passed)
                # print(sound.contains_point(self.bat.position))
            self.simulation.handle_reflections(time_passed)
            # print(f"current time: {time_passed}")
            # print(self.simulation.sound_objects)
            if time_passed < 0.005:
                if len(self.simulation.sound_objects) == 1:
                    array_with_booleans.append(True)
                else:
                    array_with_booleans.append(False)
            else:
                if len(self.simulation.sound_objects) == 2:
                    array_with_booleans.append(True)
                else:
                    array_with_booleans.append(False)

        self.assertTrue((array_with_booleans == [True] * 6))
        # print(f"POST {i}")


if __name__ == "__main__":

    unittest.main()
