"""This module handles creation of obstacles in the simualtion"""

import random

from supporting_files.vectors import Vector


class Obstacle:
    _id_counter = 0

    def __init__(self, parameters_df):
        self.id = Obstacle._id_counter
        Obstacle._id_counter += 1
        self.parameters_df = parameters_df
        self.position = Vector(
            random.uniform(
                self.parameters_df["OBSTACLE_RADIUS"][0],
                self.parameters_df["ARENA_WIDTH"][0]
                - self.parameters_df["OBSTACLE_RADIUS"][0],
            ),
            random.uniform(
                self.parameters_df["OBSTACLE_RADIUS"][0],
                self.parameters_df["ARENA_HEIGHT"][0]
                - self.parameters_df["OBSTACLE_RADIUS"][0],
            ),
        )

        self.radius = self.parameters_df["OBSTACLE_RADIUS"][0]

    # TODO: use this and implement avoidance on collision
    def check_collision(self, point):
        """checks if the given point is within the object

        Args:
            point (Vector): point to check

        Returns:
            Bool: True if the point is within the object
        """
        return self.position.distance_to(point) <= self.radius

    def get_reflection_normal(self, point):
        """the normal from a the point of reflection

        Args:
            point (Vector): point on the object

        Returns:
            Vector: normal vector from the point
        """
        return (point - self.position).normalize()
