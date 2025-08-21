"""functions to help with movmemnt of bats, integrating sound"""

import sys

import numpy as np

sys.path.append("./dynamic_model")
from supporting_files.vectors import Vector

print(np.round(0.0015, 3))


def generate_direction_vector_given_sound(self, sound):
    spl_of_sound = sound.current_spl
    normalized_sound_vector = (sound.origin - self.position).normalize()
    vector_w_spl_magnitude = normalized_sound_vector * spl_of_sound
    return vector_w_spl_magnitude


def decide_next_direction(self, detected_sound_objects):
    """decide next direction of bat based on sound

    Args:
        detected_sound_objects (list): list containing detected sounds
    """
    if len(detected_sound_objects) != 0:
        max_spl = np.max([i.current_spl for i in detected_sound_objects])
        if max_spl > 72:
            sum_of_sound_vectors = Vector(0, 0)
            for sound in detected_sound_objects:
                sum_of_sound_vectors += generate_direction_vector_given_sound(
                    self, sound
                )
            mean_vector = sum_of_sound_vectors * (1 / len(detected_sound_objects))
            if max_spl > 82:
                next_direction = mean_vector.rotate(np.pi)
                self.direction = next_direction.normalize()
            else:
                next_direction = mean_vector
                self.direction = next_direction.normalize()


x = Vector(1, 0) + Vector(0, 0) + Vector(3, 0)
print(x.normalize() * 0.5)
