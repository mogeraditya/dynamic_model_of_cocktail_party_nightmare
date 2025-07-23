from supporting_files.vectors import Vector
import random
from supporting_files.constants import Constants

class Obstacle:
    _id_counter = 0

    def __init__(self):
        self.id = Obstacle._id_counter
        Obstacle._id_counter += 1

        self.position = Vector(
            random.uniform(Constants.OBSTACLE_RADIUS, Constants.ARENA_WIDTH - Constants.OBSTACLE_RADIUS),
            random.uniform(Constants.OBSTACLE_RADIUS, Constants.ARENA_HEIGHT - Constants.OBSTACLE_RADIUS)
        )
        self.radius = Constants.OBSTACLE_RADIUS
    # TODO: use this and implement avoidance on collision
    def check_collision(self, point):
        return self.position.distance_to(point) <= self.radius

    def get_reflection_normal(self, point):
        return (point - self.position).normalize()