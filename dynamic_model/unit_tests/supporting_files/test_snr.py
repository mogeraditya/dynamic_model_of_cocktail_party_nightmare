"""unit test to test bat objects"""

import sys
import unittest
from unittest.mock import patch

import matplotlib.pyplot as plt
import numpy as np

sys.path.append("./dynamic_model")
from supporting_files.snr_implementation import (
    create_total_masking_profile,
    filter_sounds_based_on_total_profile,
    find_sum_of_db,
    generate_sound_profile,
    is_signal_heard,
    parse_sounds,
    serialize_sound_info,
    sound_within_time_interval,
)
from supporting_files.utilities import load_parameters

DIR_PARAMS = "./dynamic_model/unit_tests/params_unittest/test_bat_object.csv"


def mock_sound(
    time,
    received_spl,
    emitter_id,
    sound_type,
    reflected_from,
    sound_id,
    incident_direction,
):
    """make a mock sound for testing"""
    output = {
        "time": time,
        "origin": "doesnt matter",
        "distance_from_bat": 1,
        "received_spl": received_spl,
        "emitter_id": emitter_id,
        "type": sound_type,
        "reflected_from": reflected_from,
        "sound_object_id": sound_id,
        "sound_direction": (1, 1),
        "incident_direction": incident_direction,
        "bat_direction": (0, 1),
        "bat_position": (0, 0),
        "bat_last_call_time": 0.0,
    }
    return output


class TestingSNR(unittest.TestCase):
    def setUp(self):
        self.parameters_df = load_parameters(DIR_PARAMS)

        sound1 = mock_sound(0.01, 80, 1, "direct", 2, 123, (1, 1))
        # check if same sound id is merged together
        sound2 = mock_sound(0.02, 80, 1, "direct", 2, 123, (1, 1))
        # checks for snr threshold thingy
        sound3 = mock_sound(0.01, 30, 1, "direct", 3, 121, (1, 1))
        # checks for angle thresholding
        sound4 = mock_sound(0.01, 80, 1, "direct", 2, 124, (1, -1))
        # checks duration gating
        sound5 = mock_sound(0.07, 80, 1, "direct", 2, 125, (1, 1))

        self.mock_sound_objects = [sound1, sound2, sound3, sound4, sound5]

        self.mock_serialized_sounds = [
            {
                "sound_object_id": "sound1",
                "received_spl": 80.0,
                "time": 0.01,
                "duration": 0.005,
                "all_spl_values": [80.0, 79.0, 78.0, 77.0, 76.0],
                "bat_last_call_time": 0.0,
            },
            {
                "sound_object_id": "sound2",
                "received_spl": 75.0,
                "time": 0.012,
                "duration": 0.004,
                "all_spl_values": [75.0, 74.0, 73.0, 72.0],
                "bat_last_call_time": 0.0,
            },
        ]

    def test_parse_sounds_basic(self):
        """Test basic sound parsing with all filters"""
        result = parse_sounds(
            sound_objects=self.mock_sound_objects,
            time_threshold_post_call=0.05,
            angle_threshold=np.radians(90),
            focal_bat=0,
            include_direct_sounds=True,
            call_duration=0.005,
        )

        # should only include sounds within angle threshold and time window
        # only sound1, sound2, and sound3
        # print(result)
        self.assertEqual(len(result), 3)

    def test_parse_sounds_exclude_direct(self):
        """Test parsing when direct sounds are excluded"""
        result = parse_sounds(
            sound_objects=self.mock_sound_objects,
            time_threshold_post_call=0.05,
            angle_threshold=np.radians(45),
            focal_bat=0,
            include_direct_sounds=False,
            call_duration=0.005,
        )

        # should exclude direct sounds
        self.assertEqual(len(result), 0)

    def test_parse_sounds_angle_threshold(self):
        """Test angle threshold filtering"""
        result = parse_sounds(
            sound_objects=self.mock_sound_objects,
            time_threshold_post_call=0.05,
            angle_threshold=np.radians(180),
            focal_bat=0,
            include_direct_sounds=True,
            call_duration=0.005,
        )

        # should include more sounds with wider angle
        self.assertEqual(len(result), 4)

    def test_parse_sounds_time_threshold(self):
        """Test time threshold filtering"""

        result = parse_sounds(
            sound_objects=self.mock_sound_objects,
            time_threshold_post_call=0.071,
            angle_threshold=np.radians(180),
            focal_bat=0,
            include_direct_sounds=True,
            call_duration=0.005,
        )

        # should include more sounds/ all sounds in list
        self.assertEqual(len(result), 5)

    def test_serialize_sound_info_basic(self):
        """Test basic sound serialization"""
        result = serialize_sound_info(
            parsed_sound_objects=self.mock_sound_objects,
            sim_time_step=0.001,
            sim_rounding=3,
        )
        print(result)
        # should group by sound_object_id
        self.assertEqual(len(result), 4)

    def test_serialize_sound_info_empty_input(self):
        """Test serialization with empty input"""
        result = serialize_sound_info([], 0.001, 3)
        self.assertEqual(result, [])

    def test_serialize_sound_info_single_sound(self):
        """Test serialization with single sound instance"""
        single_sound = [self.mock_sound_objects[0]]
        result = serialize_sound_info(single_sound, 0.001, 3)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["received_spl"], 80.0)
        self.assertAlmostEqual(result[0]["duration"], 0.001)

    def test_find_sum_of_db_basic(self):
        """Test basic dB sum calculation"""
        spl_list = [80.0, 82.0, 78.0]
        result = find_sum_of_db(spl_list, 4)
        expected = 20 * np.log10(10 ** (80 / 20) + 10 ** (82 / 20) + 10 ** (78 / 20))
        self.assertAlmostEqual(result, expected, places=3)

    def test_find_sum_of_db_zeros(self):
        """Test dB sum with zero values"""
        spl_list = [0.0, 80.0, 0.0]
        result = find_sum_of_db(spl_list, 4)

        expected = 80.0
        self.assertAlmostEqual(result, expected)

    def test_find_sum_of_db_single_value(self):
        """Test dB sum with single value"""
        spl_list = [85.0]
        result = find_sum_of_db(spl_list, 4)

        self.assertEqual(result, 85.0)

    def test_sound_within_time_interval_inside(self):
        """Test sound inside time interval"""
        sound = {"time": 0.05}
        time_interval = [0.0, 0.1]

        result = sound_within_time_interval(sound, time_interval)
        self.assertTrue(result)

    def test_sound_within_time_interval_after(self):
        """Test sound after time interval"""
        sound = {"time": 0.11}
        time_interval = [0.0, 0.1]

        result = sound_within_time_interval(sound, time_interval)
        self.assertFalse(result)

    def test_sound_within_time_interval_boundary(self):
        """Test sound at boundary of time interval"""
        sound = {"time": 0.1}
        time_interval = [0.0, 0.1]

        result = sound_within_time_interval(sound, time_interval)
        self.assertFalse(result)

    def test_create_total_masking_profile_basic(self):
        """Test basic masking profile creation"""
        time_axis, total_profile = create_total_masking_profile(
            self.mock_serialized_sounds, 0.001, 3
        )

        self.assertEqual(len(time_axis), len(total_profile))
        self.assertGreater(len(time_axis), 0)
        self.assertEqual(time_axis[0], 0.0)
        self.assertGreaterEqual(time_axis[-1], 0.015)

    def test_create_total_masking_profile_empty(self):
        """Test masking profile with empty input"""
        with self.assertRaises(IndexError):
            create_total_masking_profile([], 0.001, 4)


class TestFilterSoundsBasedOnTotalProfile(unittest.TestCase):
    def setUp(self):
        self.mock_serialized_sounds = [
            {
                "sound_object_id": 110,
                "received_spl": 80.0,
                "time": 0.01,
                "duration": 0.005,
                "all_spl_values": [80.0] * 5,
            },
            {
                "sound_object_id": 111,
                "received_spl": 40.0,
                "time": 0.012,
                "duration": 0.004,
                "all_spl_values": [40.0] * 4,
            },
        ]

    @patch("supporting_files.snr_implementation.create_total_masking_profile")
    def test_filter_sounds_based_on_total_profile(self, mock_profile):
        """Test sound filtering based on total profile"""

        mock_profile.return_value = (
            np.array([0.01, 0.011, 0.012, 0.013]),
            np.array([80.0, 80.0, 80.0, 80.0]),
        )

        result = filter_sounds_based_on_total_profile(
            self.mock_serialized_sounds, 0.001, 3
        )

        # quiet sound should be filtered
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["sound_object_id"], 110)


class TestGenerateSoundProfile(unittest.TestCase):
    def setUp(self):
        self.mock_focal_sound = {
            "sound_object_id": "focal",
            "received_spl": 80.0,
            "time": 0.02,
            "duration": 0.005,
            "bat_last_call_time": 0.0,
        }

        self.mock_other_sounds = [
            {
                "sound_object_id": "masker1",
                "received_spl": 75.0,
                "time": 0.018,
                "duration": 0.004,
                "all_spl_values": [75.0, 74.0, 73.0, 72.0],
            },
            {
                "sound_object_id": "masker2",
                "received_spl": 70.0,
                "time": 0.025,
                "duration": 0.003,
                "all_spl_values": [70.0, 69.0, 68.0],
            },
        ]

    def test_generate_sound_profile_basic(self):
        """Test basic sound profile generation"""
        ratio, time_axis = generate_sound_profile(
            self.mock_other_sounds,
            self.mock_focal_sound,
            [0.025, -0.001],
            0.001,
            4,
        )

        self.assertEqual(len(ratio), len(time_axis))
        self.assertGreater(len(time_axis), 0)
        self.assertTrue(all(not np.isnan(x) for x in ratio))

    def test_generate_sound_profile_no_maskers(self):
        """Test profile generation with no maskers"""
        ratio, time_axis = generate_sound_profile(
            [], self.mock_focal_sound, [0.025, -0.001], 0.001, 4
        )
        expected_ratio = np.ones_like(time_axis) * self.mock_focal_sound["received_spl"]
        np.testing.assert_array_almost_equal(ratio, expected_ratio)


class TestIsSignalHeard(unittest.TestCase):
    def setUp(self):
        """Create a mock temporal masking CSV file"""
        self.dir_of_temporal_masking_fn_file = (
            "./dynamic_model/unit_tests/params_unittest/temporal_masking_fn.csv"
        )

        self.mock_other_sounds = [
            {
                "sound_object_id": "masker1",
                "received_spl": 75.0,
                "time": 0.018,
                "duration": 0.004,
                "all_spl_values": [75.0, 74.0, 73.0, 72.0],
            },
            {
                "sound_object_id": "masker2",
                "received_spl": 70.0,
                "time": 0.025,
                "duration": 0.003,
                "all_spl_values": [70.0, 69.0, 68.0],
            },
        ]

    @patch("supporting_files.snr_implementation.generate_sound_profile")
    def test_is_signal_heard_detected(self, mock_profile):
        """Test signal detection when above threshold"""
        focal_sound = {
            "sound_object_id": "focal",
            "received_spl": 80.0,
            "time": 0.02,
            "duration": 0.005,
            "bat_last_call_time": 0.0,
        }

        mock_profile.return_value = (
            np.ones(10) * 10.0,
            np.linspace(-0.01, 0.01, 10),
        )

        result = is_signal_heard(
            focal_sound,
            self.mock_other_sounds,
            self.dir_of_temporal_masking_fn_file,
            0.75,
            0.001,
            3,
        )
        self.assertTrue(result)

    @patch("supporting_files.snr_implementation.generate_sound_profile")
    def test_is_signal_heard_not_detected(self, mock_profile):
        """Test signal non-detection when below threshold"""
        focal_sound = {
            "sound_object_id": "focal",
            "received_spl": 80.0,
            "time": 0.02,
            "duration": 0.005,
            "bat_last_call_time": 0.0,
        }

        mock_profile.return_value = (
            np.ones(10) * -10.0,
            np.linspace(-0.01, 0.01, 10),
        )
        result = is_signal_heard(
            focal_sound,
            self.mock_other_sounds,
            self.dir_of_temporal_masking_fn_file,
            0.75,
            0.001,
            3,
        )
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
