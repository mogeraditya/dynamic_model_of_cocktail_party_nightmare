from supporting_files.vectors import Vector
import random


class Obstacle:
    _id_counter = 0

    def __init__(self, parameters_df):
        self.id = Obstacle._id_counter
        Obstacle._id_counter += 1
        self.parameters_df= parameters_df
        self.position = Vector(
            random.uniform(self.parameters_df['OBSTACLE_RADIUS'], self.parameters_dict["ARENA_WIDTH"] - self.parameters_df['OBSTACLE_RADIUS']),
            random.uniform(self.parameters_df['OBSTACLE_RADIUS'], self.parameters_dict["ARENA_HEIGHT"] - self.parameters_df['OBSTACLE_RADIUS'])
        )
        self.radius = self.parameters_df['OBSTACLE_RADIUS']
    # TODO: use this and implement avoidance on collision
    def check_collision(self, point):
        return self.position.distance_to(point) <= self.radius

    def get_reflection_normal(self, point):
        return (point - self.position).normalize()