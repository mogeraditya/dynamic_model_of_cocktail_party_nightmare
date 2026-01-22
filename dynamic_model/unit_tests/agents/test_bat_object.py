"""Unittests for bat object in agents.bats"""

import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np

sys.path.append("./dynamic_model")

from supporting_files.utilities import load_parameters
from supporting_files.vectors import Vector

from dynamic_model.agents.class_bats import Bat
from dynamic_model.agents.class_sounds import DirectSound

Bat._id_counter = 0
print(os.getcwd())
DIR_PARAMS = "./dynamic_model/unit_tests/params_unittest/test_bat_object.csv"


class TestBatObject(unittest.TestCase):

    def setUp(self):
        self.mock_parameters = load_parameters(DIR_PARAMS)
        with tempfile.TemporaryDirectory() as temp_dir:
            self.bat = Bat(self.mock_parameters, temp_dir)
            self.bat.id = 0
        return super().setUp()

    def test_bat_initialization(self):
        """check the initialization of self.bat objects."""

        self.assertTrue(self.bat.id == 0)
        self.assertTrue(isinstance(self.bat.position, Vector))
        self.assertTrue(isinstance(self.bat.direction, Vector))
        self.assertTrue(self.bat.speed == self.mock_parameters["BAT_SPEED"])
        self.assertTrue(self.bat.radius == self.mock_parameters["BAT_RADIUS"])
        self.assertTrue(self.bat.implement_snr is True)
        self.assertTrue(len(self.bat.emitted_sounds) == 0)
        self.assertTrue(len(self.bat.received_sounds) == 0)

    def test_self_id_counter(self):
        """check if id counter works as intend"""
        with tempfile.TemporaryDirectory() as temp_dir:
            Bat._id_counter = 0
            bat0 = Bat(self.mock_parameters, temp_dir)
            bat1 = Bat(self.mock_parameters, temp_dir)

            self.assertTrue(bat0.id == 0)
            self.assertTrue(bat1.id == 1)

    def test_update_movement(self):
        """check if movement step is working as intended."""
        initial_position = Vector(self.bat.position.x, self.bat.position.y)
        initial_direction = Vector(self.bat.direction.x, self.bat.direction.y)
        self.bat.update_movement()
        expected_position = (
            initial_position
            + initial_direction * self.bat.speed * self.bat.parameters_df["TIME_STEP"]
        )
        # print(self.bat.position, expected_position)
        self.assertAlmostEqual(self.bat.position.x, expected_position.x)
        self.assertAlmostEqual(self.bat.position.y, expected_position.y)

    def test_update_movement_boundary_bounce(self):
        """Test self.bat bounces off walls and all correctly"""
        # make the self.bat hit the left wall
        self.bat.position = Vector(0, 1)
        self.bat.direction = Vector(-1, 0)
        self.bat.update_movement()

        # direction should be reverse after hitting boundary
        self.assertTrue(self.bat.direction.x == 1)
        self.assertTrue(self.bat.direction.y == 0)  # y shouldnt chnage
        self.assertTrue(self.bat.next_direction.x == 1)
        self.assertTrue(
            (self.bat.next_direction.y == 0)
        )  # next direction equal to current direction

    def test_emit_sounds_creation(self):
        """check if sound emitted wgen time threshold crosses."""
        current_time = 1.0
        sound_objects = []

        # Set time since last call to exceed call interval
        self.bat.time_since_last_call = (
            1.0 / self.bat.parameters_df["CALL_RATE"] + 0.001
        )

        self.bat.emit_sounds(current_time, sound_objects)

        # if sound created, len non zero
        self.assertTrue(len(self.bat.emitted_sounds) == 1)
        self.assertTrue(len(sound_objects) == 1)
        self.assertTrue(self.bat.emit_times[-1] == current_time)
        self.assertTrue(
            self.bat.time_since_last_call != 0
        )  # there should be noise ideally

    def test_emit_sounds_no_emission(self):
        """no sound should be emitted when call interval not reached"""
        current_time = 1.0
        sound_objects = []
        initial_emit_count = len(self.bat.emitted_sounds)

        # time since last call less than call interval
        self.bat.time_since_last_call = (
            1.0 / self.bat.parameters_df["CALL_RATE"] - 0.002
        )

        self.bat.emit_sounds(current_time, sound_objects)

        # check that no sound was emitted
        self.assertTrue(len(self.bat.emitted_sounds) == initial_emit_count)
        self.assertTrue(len(sound_objects) == 0)

    def test_convert_sound_to_dictionary(self):
        """check if sound serailized properly"""

        mock_sound = Mock()
        mock_sound.origin = Vector(10, 10)
        mock_sound.emitter_id = 1
        mock_sound.direction_vector = Vector(1, 0)
        mock_sound.reflected_from = None
        mock_sound.id = 123

        current_time = 1.0
        received_spl = 80.0

        with patch("agents.sounds.DirectSound", return_value=Mock()):
            mock_sound.__class__ = DirectSound
            result = self.bat.convert_sound_to_dictionary(
                mock_sound, current_time, received_spl
            )

        expected_keys = [
            "time",
            "origin",
            "distance_from_bat",
            "received_spl",
            "emitter_id",
            "type",
            "reflection_count",
            "reflected_from",
            "sound_object_id",
            "sound_direction",
            "incident_direction",
            "bat_direction",
            "bat_position",
            "bat_last_call_time",
        ]

        for key in expected_keys:
            self.assertTrue(key in result)

        self.assertTrue(result["time"] == current_time)
        self.assertTrue(result["received_spl"] == received_spl)
        self.assertTrue(result["emitter_id"] == 1)
        self.assertTrue(result["type"] == "direct")

    def test_sound_detection(self):
        """Test the sound detection"""

        origin = Vector(0, 0)
        creation_time = 0
        parameters_df = load_parameters(DIR_PARAMS)

        sound_disk_width = self.bat.parameters_df["SOUND_DISK_WIDTH"]

        self.bat.position = origin
        sound1 = DirectSound(
            parameters_df=parameters_df,
            origin=Vector(-sound_disk_width + 0.0001, 0),
            creation_time=creation_time,
            emitter_id="sound1",
            direction_vector=self.bat.direction,
        )
        sound2 = DirectSound(
            parameters_df=parameters_df,
            origin=Vector(-3 * sound_disk_width + 0.0001, 0),
            creation_time=creation_time,
            emitter_id="sound2",
            direction_vector=self.bat.direction,
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

        self.assertTrue(array_with_booleans == expected_output)

    def test_generate_direction_vector_given_sound(self):
        """Test direction vector generation from sound,"""
        sound_dict = {"received_spl": 80.0, "origin": (20, 30)}

        self.bat.position = Vector(10, 10)

        result = self.bat.generate_direction_vector_given_sound(sound_dict)

        self.assertTrue(isinstance(result, Vector))
        # next direction should point from self.bat position to sound origin
        expected_direction = (Vector(20, 30) - self.bat.position).normalize() * 80
        self.assertAlmostEqual(result.x, expected_direction.x)
        self.assertAlmostEqual(result.y, expected_direction.y)

    def test_rotate_towards_given_degree(self):
        """Test rotation towards target direction"""
        initial_direction = Vector(1, 0)
        self.bat.direction = initial_direction

        target_direction = Vector(0, 1)
        rotation_rate = np.pi / 2  # unhinged ik ik ik ik

        self.bat.rotate_towards_given_degree(target_direction, rotation_rate)

        self.assertTrue(self.bat.direction != initial_direction)
        self.assertAlmostEqual(self.bat.direction.x, target_direction.x)
        self.assertAlmostEqual(self.bat.direction.y, target_direction.y)
        self.assertAlmostEqual(self.bat.direction.magnitude(), 1.0)

        new_target_direction = Vector(0, -1)
        self.bat.rotate_towards_given_degree(new_target_direction, rotation_rate)
        self.assertTrue(self.bat.direction != initial_direction)
        self.assertNotAlmostEqual(self.bat.direction.x, new_target_direction.x)
        self.assertNotAlmostEqual(self.bat.direction.y, new_target_direction.y)
        self.assertAlmostEqual(self.bat.direction.magnitude(), 1.0)

    def test_decide_next_direction_unsupported_rule(self):
        """Test error handling for unsupported behavior rule"""
        self.mock_parameters["BEHAVIOUR_RULE"] = ["quiztopher komban"]
        self.bat.parameters_df = self.mock_parameters
        with self.assertRaises(Exception) as context:
            self.bat.decide_next_direction([])
        self.assertTrue("unsupported behaviour rule" in str(context.exception))

    def test_cleanup_sounds(self):
        """Test sound data cleanup and saving"""
        current_time = 100.0

        self.bat.received_sounds = [{"time": 1.0, "data": "test"}]
        self.bat.emitted_sounds = [{"time": 1.0, "data": "test"}]
        self.bat.time_since_last_cleanup = 0

        self.bat.cleanup_sounds(current_time)

        # check that lists were cleared
        self.assertTrue(len(self.bat.received_sounds) == 0)
        self.assertTrue(len(self.bat.emitted_sounds) == 0)
        self.assertTrue(self.bat.time_since_last_cleanup == -np.inf)

    def test_repr(self):
        """Test string representation"""
        representation = repr(self.bat)
        self.assertTrue(f"Bat(id={self.bat.id}" in representation)
        self.assertTrue("position=" in representation)


if __name__ == "__main__":
    unittest.main()
