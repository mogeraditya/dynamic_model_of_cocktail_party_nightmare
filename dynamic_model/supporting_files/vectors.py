# we need to encode vectors, points as objects in order to make them compatible with other objects

import math
import random


class Vector:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def compare(self, other):
        """Compare two vectors

        Args:
            other (Vector): the other vector being compared to

        Returns:
            Boolean: true if same else false
        """
        if self.x == other.x and self.y == other.y:
            return True
        else:
            return False

    def magnitude(self):
        """computed magnitude of vectors

        Returns:
            float: magnitude of the vector
        """
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        """normalizes the vector

        Returns:
            Vector: normalized vector
        """
        mag = self.magnitude()
        if mag > 0:
            return Vector(self.x / mag, self.y / mag)
        return Vector()

    def distance_to(self, other):
        """measure distance between two vectors

        Args:
            other (Vector): compute distance to this vector

        Returns:
            float: distance
        """
        return (self - other).magnitude()

    def angle_between(self, other):
        """measure angle difference between two vectors

        Args:
            other (Vector): compute distance to this vector

        Returns:
            float: angle in radians
        """
        angle = math.degrees(math.atan2(other.y, other.x) - math.atan2(self.y, self.x))
        return math.radians((angle + 180) % 360 - 180)
        # dot_product = self.x * other.x + self.y * other.y
        # product_of_magnitudes = self.magnitude() * other.magnitude()

        # return math.acos(dot_product / product_of_magnitudes)

    def random_direction(self):
        """generate a random vector

        Returns:
            Vector: Vector with random direction
        """
        angle = random.uniform(0, 2 * math.pi)
        return Vector(math.cos(angle), math.sin(angle))

    def reflect(self, normal):
        """find the reflection of a vector about a point

        Args:
            normal (Vector): normal vector about which the reflection is done

        Returns:
            Vector: reflection
        """
        normal = normal.normalize()
        dot_product = self.x * normal.x + self.y * normal.y
        return self - normal * (2 * dot_product)

    def to_tuple(self):
        """convert Vector to tuple

        Returns:
            tuple: output tuple
        """
        return (self.x, self.y)

    def rotate(self, angle):
        """rotate a vector

        Args:
            angle (float): angle in radians

        Returns:
            Vector: new rotated vector
        """
        new_x = self.x * math.cos(angle) - self.y * math.sin(angle)
        new_y = self.x * math.sin(angle) + self.y * math.cos(angle)
        return Vector(new_x, new_y)

    def __repr__(self):
        return f"Vector({self.x:.3f}, {self.y:.3f})"
