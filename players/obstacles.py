from supporting_files.vectors import Vector
import random
from supporting_files.constants import Constants

class Obstacle:
    def __init__(self):
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