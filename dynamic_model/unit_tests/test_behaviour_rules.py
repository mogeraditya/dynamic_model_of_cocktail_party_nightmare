import os
import sys
import unittest

import numpy as np

sys.path.append("./dynamic_model")

from supporting_files.utilities import (
    convert_detected_sounds_into_grids,
    convert_matrix_to_one_hot,
    given_matrix_find_cell_to_respond_to,
    given_time_and_angle_return_direction,
    load_parameters,
)
from supporting_files.vectors import Vector

print(os.getcwd())
DIR_PARAMS = "./dynamic_model/unit_tests/params_unittest/test_sound_propagation.csv"


class TestConvertMatrixToOneHot(unittest.TestCase):
    def test_convert_matrix_to_one_hot_positive_values(self):
        """Test conversion of matrix with positive values to one-hot"""
        input_matrix = np.array([[0, 2, 0], [1, 0, 3], [0, 0, 0]])
        expected = np.array([[0, 1, 0], [1, 0, 1], [0, 0, 0]])
        result = convert_matrix_to_one_hot(input_matrix)
        np.testing.assert_array_equal(result, expected)

    def test_convert_matrix_to_one_hot_all_zeros(self):
        """Test conversion of matrix with all zeros"""
        input_matrix = np.zeros((3, 3))
        expected = np.zeros((3, 3))
        result = convert_matrix_to_one_hot(input_matrix)
        np.testing.assert_array_equal(result, expected)

    def test_convert_matrix_to_one_hot_all_positive(self):
        """Test conversion of matrix with all positive values"""
        input_matrix = np.array([[1, 2], [3, 4]])
        expected = np.array([[1, 1], [1, 1]])
        result = convert_matrix_to_one_hot(input_matrix)
        np.testing.assert_array_equal(result, expected)


class TestGivenMatrixFindCellToRespondTo(unittest.TestCase):
    def test_given_matrix_find_cell_to_respond_to_with_activations(self):
        """Test finding cell to respond to with multiple activations"""
        matrix = np.array([[0, 2, 0], [3, 1, 4], [0, 0, 5]])
        threshold = 2
        result = given_matrix_find_cell_to_respond_to(matrix, threshold)

        expected = [0, 1]
        print(result)
        self.assertTrue((result == expected).all())

    def test_given_matrix_find_cell_to_respond_to_no_activations(self):
        """Test finding cell when no cells meet threshold"""
        matrix = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
        threshold = 2
        result = given_matrix_find_cell_to_respond_to(matrix, threshold)
        self.assertIsNone(result)

    def test_given_matrix_find_cell_to_respond_to_single_activation(self):
        """Test finding cell with single activation"""
        matrix = np.array([[0, 0, 0], [0, 3, 0], [0, 0, 0]])
        threshold = 2
        result = given_matrix_find_cell_to_respond_to(matrix, threshold)
        expected = [1, 1]
        self.assertTrue((result == expected).all())

    def test_given_matrix_find_cell_to_respond_to_multiple_first_row(self):
        """Test finding cell when multiple activations in first row"""
        matrix = np.array([[3, 2, 4], [1, 1, 1], [1, 1, 1]])
        threshold = 2
        result = given_matrix_find_cell_to_respond_to(matrix, threshold)

        expected = [0, 1]
        self.assertTrue((result == expected).all())


class TestConvertDetectedSoundsIntoGrids(unittest.TestCase):
    def setUp(self):
        """Set up test parameters and mock data"""
        self.parameters_df = load_parameters(DIR_PARAMS)

        self.allocentric_axis_y = Vector(0, 1)
        self.mock_heard_sounds = [
            {
                "occurance_times": [0.015],
                "bat_last_call_time": 0.0,
                "incident_direction": Vector(0.5, 0.5),
                "bat_direction": Vector(1, 0),
            },
            {
                "occurance_times": [0.025],
                "bat_last_call_time": 0.0,
                "incident_direction": Vector(-0.5, 0.5),
                "bat_direction": Vector(1, 0),
            },
        ]

    def test_convert_detected_sounds_into_grids_egocentric(self):
        """Test grid conversion with egocentric reference frame"""
        grid, grid_r, grid_theta = convert_detected_sounds_into_grids(
            self.mock_heard_sounds, self.parameters_df, self.allocentric_axis_y
        )

        self.assertEqual(grid.shape, (len(grid_r), len(grid_theta)))
        self.assertGreater(np.sum(grid), 0)

    def test_convert_detected_sounds_into_grids_allocentric(self):
        """Test grid conversion with allocentric reference frame"""

        grid, grid_r, grid_theta = convert_detected_sounds_into_grids(
            self.mock_heard_sounds, self.parameters_df, self.allocentric_axis_y
        )

        self.assertEqual(grid.shape, (len(grid_r), len(grid_theta)))
        self.assertGreater(np.sum(grid), 0)

    def test_convert_detected_sounds_into_grids_one_hot(self):
        """Test grid conversion with one-hot encoding"""

        grid = convert_detected_sounds_into_grids(
            self.mock_heard_sounds, self.parameters_df, self.allocentric_axis_y
        )[0]

        # all non-zero values should be 1
        self.assertTrue(np.all(np.logical_or(grid == 0, grid == 1)))

    def test_convert_detected_sounds_into_grids_empty(self):
        """Test grid conversion with empty sound list"""
        grid = convert_detected_sounds_into_grids(
            [], self.parameters_df, self.allocentric_axis_y
        )[0]

        self.assertEqual(np.sum(grid), 0)

    def test_convert_detected_sounds_into_grids_unsupported_reference_frame(self):
        """Test grid conversion with unsupported reference frame"""
        self.parameters_df["SPATIAL_REFERENCE_FRAME"] = "tukun babu"
        with self.assertRaises(ValueError):
            convert_detected_sounds_into_grids(
                self.mock_heard_sounds, self.parameters_df, self.allocentric_axis_y
            )


class TestGivenTimeAndAngleReturnDirection(unittest.TestCase):
    def setUp(self):
        """Set up test parameters"""
        self.parameters_df = load_parameters(DIR_PARAMS)

        self.bat_direction = Vector(1, 0)
        self.allocentric_axis_y = Vector(0, 1)

    def test_given_time_and_angle_return_direction_repulsion(self):
        """Test direction calculation for repulsion (short time delay)"""
        time_delay = 0.005
        angle = np.pi / 4
        next_direction, response_type = given_time_and_angle_return_direction(
            time_delay,
            angle,
            self.parameters_df,
            self.bat_direction,
            self.allocentric_axis_y,
        )

        self.assertEqual(response_type, "repulsion")
        self.assertIsInstance(next_direction, Vector)
        self.assertAlmostEqual(next_direction.magnitude(), 1.0)

    def test_given_time_and_angle_return_direction_attraction(self):
        """Test direction calculation for attraction (long time delay)"""
        time_delay = 0.015
        angle = np.pi / 4

        next_direction, response_type = given_time_and_angle_return_direction(
            time_delay,
            angle,
            self.parameters_df,
            self.bat_direction,
            self.allocentric_axis_y,
        )

        self.assertEqual(response_type, "attraction")
        self.assertIsInstance(next_direction, Vector)
        self.assertAlmostEqual(next_direction.magnitude(), 1.0)

    def test_given_time_and_angle_return_direction_allocentric(self):
        """Test direction calculation with allocentric reference frame"""

        time_delay = 0.025
        angle = np.pi / 4

        next_direction, response_type = given_time_and_angle_return_direction(
            time_delay,
            angle,
            self.parameters_df,
            self.bat_direction,
            self.allocentric_axis_y,
        )

        self.assertEqual(response_type, "attraction")
        self.assertIsInstance(next_direction, Vector)


if __name__ == "__main__":

    unittest.main()
