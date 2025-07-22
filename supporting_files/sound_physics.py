from supporting_files.vectors import Vector2D
import math
from supporting_files.constants import Constants

class Physics:

    @staticmethod #because they dont act on the class objects themselves
    def calculate_spherical_energy(initial_energy, distance):
        """Calculate sound energy with spherical spreading and attenuation"""
        if distance <= 0:
            return initial_energy
        # Inverse square law with additional attenuation
        energy = initial_energy / (4 * math.pi * distance**2)
        energy *= math.exp(-distance * Constants.SOUND_DECAY_RATE)
        return energy
    
    @staticmethod
    def get_reflection_normal(point, obstacle):
        """Get reflection normal for obstacle or wall"""
        if hasattr(obstacle, 'radius'):  # It's a circular obstacle
            return (point - obstacle.position).normalize()
        # TODO: fix the reflection off of walls, there is some issue
        else:  # It's a wall
            # Determine which wall was hit
            x, y = point.x, point.y
            if x <= 0:
                return Vector2D(1, 0)
            elif x >= Constants.ARENA_WIDTH:
                return Vector2D(-1, 0)
            elif y <= 0:
                return Vector2D(0, 1)
            elif y >= Constants.ARENA_HEIGHT:
                return Vector2D(0, -1)
            return Vector2D(0, 0)  # Shouldn't happen
    
    @staticmethod
    def is_point_in_arena(point):
        """Check if a point is within arena boundaries"""
        return (0 <= point.x <= Constants.ARENA_WIDTH and 
                0 <= point.y <= Constants.ARENA_HEIGHT)
    
    @staticmethod
    def is_sound_in_arena(sound):
        