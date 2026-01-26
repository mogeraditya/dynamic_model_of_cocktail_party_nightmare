"""This module handles creation of obstacles in the simualtion"""

import random

from supporting_files.vectors import Vector


class Obstacle:
    _id_counter = 0

    def __init__(self, parameters_df, position, radius):
        self.id = Obstacle._id_counter
        Obstacle._id_counter += 1
        self.parameters_df = parameters_df
        if position == "random":
            self.position = Vector(
                random.uniform(
                    self.parameters_df["OBSTACLE_RADIUS"],
                    self.parameters_df["ARENA_WIDTH"]
                    - self.parameters_df["OBSTACLE_RADIUS"],
                ),
                random.uniform(
                    self.parameters_df["OBSTACLE_RADIUS"],
                    self.parameters_df["ARENA_LENGTH"]
                    - self.parameters_df["OBSTACLE_RADIUS"],
                ),
            )
        else:
            self.position = Vector(position[0], position[1])
        self.radius = radius  #

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
