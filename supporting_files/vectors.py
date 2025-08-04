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
    
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector(self.x/mag, self.y/mag)
        return Vector()
    
    def distance_to(self, other):
        return (self - other).magnitude()
    
    def random_direction(self):
        angle = random.uniform(0, 2 * math.pi)
        return Vector(math.cos(angle), math.sin(angle))
    
    def reflect(self, normal):
        normal = normal.normalize()
        dot_product = self.x * normal.x + self.y * normal.y
        return self - normal * (2 * dot_product)
    
    def to_tuple(self):
        return (self.x, self.y)
    
    # def __repr__(self):
    #     return f'Vector({self.x:.2f}, {self.y:.2f})'