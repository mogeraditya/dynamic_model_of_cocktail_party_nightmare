import os
import sys
import tempfile
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest

# Add the path to your modules
sys.path.append("./dynamic_model")

from agents.bats import Bat
from agents.sounds import DirectSound
from supporting_files.utilities import load_parameters
from supporting_files.vectors import Vector

Bat._id_counter = 0
print(os.getcwd())
DIR_PARAMS = "./dynamic_model/unit_tests/params_unittest/test_bat_object.csv"
OUTPUT_DIR = "./dynamic_model/unit_tests/detection_files/"


class TestBatObject:
    # def __init__(self):
    #     self.origin = Vector(0, 0)
    #     self.origin = Vector(0, 0)
    #     self.creation_time = 0

    #     self.parameters_df = load_parameters(DIR_PARAMS)
    # self.bat = Bat(self.parameters_df, output_dir=OUTPUT_DIR)

    def reset_bat_counter(self):
        """Reset the counter of bat object when needed."""
        Bat._id_counter = 0

    @pytest.fixture
    def mock_parameters(self):
        """load mock parameters for the test.

        Returns:
            DataFrame: the mock dataframe for the tests.
        """
        parameters_df = load_parameters(DIR_PARAMS)
        return parameters_df

    @pytest.fixture
    def bat(self, mock_parameters):
        """create bat object using mock parameters and id 0.

        Args:
            mock_parameters (DataFrame): dataframe containing bat parameters.

        Returns:
            Bat : Bat object with id 0
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            bat = Bat(mock_parameters, temp_dir)
            bat.id = 0
            return bat

    def test_bat_initialization(self, mock_parameters, bat):
        """check the initialization of bat objects.

        Args:
            mock_parameters (DataFrame): dataframe containing bat parameters.
            bat (Bat): Bat object with id 0
        """

        assert bat.id == 0
        assert isinstance(bat.position, Vector)
        assert isinstance(bat.direction, Vector)
        assert bat.speed == mock_parameters["BAT_SPEED"][0]
        assert bat.radius == mock_parameters["BAT_RADIUS"][0]
        assert bat.implement_snr is True
        assert len(bat.emitted_sounds) == 0
        assert len(bat.received_sounds) == 0

    def test_bat_id_counter(self, mock_parameters):
        """check if id counter works as intend

        Args:
            mock_parameters (DataFrame): dataframe containing bat parameters.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            self.reset_bat_counter()
            bat0 = Bat(mock_parameters, temp_dir)
            bat1 = Bat(mock_parameters, temp_dir)

            assert bat0.id == 0
            assert bat1.id == 1

    def test_update_movement(self, bat):
        """check if movement step is working as intended.

        Args:
            bat (Bat): Bat object to test
        """
        initial_position = Vector(bat.position.x, bat.position.y)
        initial_direction = Vector(bat.direction.x, bat.direction.y)
        bat.update_movement()
        expected_position = (
            initial_position
            + initial_direction * bat.speed * bat.parameters_df["TIME_STEP"][0]
        )
        print(bat.position, expected_position)
        assert bat.position.x == pytest.approx(expected_position.x)
        assert bat.position.y == pytest.approx(expected_position.y)

    def test_update_movement_boundary_bounce(self, bat):
        """Test bat bounces off walls and all correctly

        Args:
            bat (Bat): Bat object to test
        """
        # make the bat hit the left wall
        bat.position = Vector(0, 1)
        bat.direction = Vector(-1, 0)
        bat.update_movement()

        # direction should be reverse after hitting boundary
        assert bat.direction.x == 1
        assert bat.direction.y == 0  # y shouldnt chnage
        assert bat.next_direction.x == 1
        assert bat.next_direction.y == 0  # next direction equal to current direction

    def test_emit_sounds_creation(self, bat):
        """check if sound emitted wgen time threshold crosses.

        Args:
            bat (Bat): Bat object to test
        """
        current_time = 1.0
        sound_objects = []

        # Set time since last call to exceed call interval
        bat.time_since_last_call = 1.0 / bat.parameters_df["CALL_RATE"][0] + 0.001

        bat.emit_sounds(current_time, sound_objects)

        # if sound created, len non zero
        assert len(bat.emitted_sounds) == 1
        assert len(sound_objects) == 1
        assert bat.emit_times[-1] == current_time
        assert bat.time_since_last_call != 0  # there should be noise ideally

    def test_emit_sounds_no_emission(self, bat):
        """no sound should be emitted when call interval not reached

        Args:
            bat (Bat): Bat object to test
        """
        current_time = 1.0
        sound_objects = []
        initial_emit_count = len(bat.emitted_sounds)

        # time since last call less than call interval
        bat.time_since_last_call = 1.0 / bat.parameters_df["CALL_RATE"][0] - 0.002

        bat.emit_sounds(current_time, sound_objects)

        # check that no sound was emitted
        assert len(bat.emitted_sounds) == initial_emit_count
        assert len(sound_objects) == 0

    def test_convert_sound_to_dictionary(self, bat):
        """check if sound serailized properly

        Args:
            bat (Bat): Bat object to test
        """

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
            result = bat.convert_sound_to_dictionary(
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
            assert key in result

        assert result["time"] == current_time
        assert result["received_spl"] == received_spl
        assert result["emitter_id"] == 1
        assert result["type"] == "direct"

    def test_sound_detection(self, bat):
        """Test the sound detection

        Args:
            bat (Bat): Bat object to test
        """

        origin = Vector(0, 0)
        creation_time = 0
        parameters_df = load_parameters(DIR_PARAMS)

        sound_disk_width = bat.parameters_df["SOUND_DISK_WIDTH"][0]

        bat.position = origin
        sound1 = DirectSound(
            parameters_df=parameters_df,
            origin=Vector(-sound_disk_width + 0.0001, 0),
            creation_time=creation_time,
            emitter_id="sound1",
            direction_vector=bat.direction,
        )
        sound2 = DirectSound(
            parameters_df=parameters_df,
            origin=Vector(-3 * sound_disk_width + 0.0001, 0),
            creation_time=creation_time,
            emitter_id="sound2",
            direction_vector=bat.direction,
        )

        times_to_inspect = np.arange(0, 0.025, 0.0025)
        array_with_booleans = []
        for time_passed in times_to_inspect:
            sound1.update(time_passed)
            sound2.update(time_passed)
            bat.detect_sounds(time_passed, [sound1, sound2])

            if len(bat.received_sounds) > 0:
                array_with_booleans.append("detected")
            else:
                array_with_booleans.append("not detected")
            bat.received_sounds = []

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

        assert array_with_booleans == expected_output

    def test_generate_direction_vector_given_sound(self, bat):
        """Test direction vector generation from sound,

        Args:
            bat (Bat): Bat object to test
        """
        sound_dict = {"received_spl": 80.0, "origin": (20, 30)}

        bat.position = Vector(10, 10)

        result = bat.generate_direction_vector_given_sound(sound_dict)

        assert isinstance(result, Vector)
        # next direction should point from bat position to sound origin
        expected_direction = (Vector(20, 30) - bat.position).normalize() * 80
        assert result.x == pytest.approx(expected_direction.x)
        assert result.y == pytest.approx(expected_direction.y)

    def test_rotate_towards_given_degree(self, bat):
        """Test rotation towards target direction"""
        initial_direction = Vector(1, 0)
        bat.direction = initial_direction

        target_direction = Vector(0, 1)
        rotation_rate = np.pi / 2  # unhinged ik ik ik ik

        bat.rotate_towards_given_degree(target_direction, rotation_rate)

        assert bat.direction != initial_direction
        assert bat.direction.x == pytest.approx(target_direction.x)
        assert bat.direction.y == pytest.approx(target_direction.y)
        assert bat.direction.magnitude() == pytest.approx(1.0)

    def test_decide_next_direction_unsupported_rule(self, bat, mock_parameters):
        """Test error handling for unsupported behavior rule"""
        mock_parameters["BEHAVIOUR_RULE"] = ["quiztopher komban"]
        bat.parameters_df = mock_parameters

        with pytest.raises(ValueError, match="unsupported behaviour rule"):
            bat.decide_next_direction([])

    def test_cleanup_sounds(self, bat):
        """Test sound data cleanup and saving"""
        current_time = 100.0

        bat.received_sounds = [{"time": 1.0, "data": "test"}]
        bat.emitted_sounds = [{"time": 1.0, "data": "test"}]
        bat.time_since_last_cleanup = 0

        bat.cleanup_sounds(current_time)

        # check that lists were cleared
        assert len(bat.received_sounds) == 0
        assert len(bat.emitted_sounds) == 0
        assert bat.time_since_last_cleanup == -np.inf

    def test_repr(self, bat):
        """Test string representation"""
        representation = repr(bat)
        assert f"Bat(id={bat.id}" in representation
        assert "position=" in representation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
