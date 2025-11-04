# this file should implement the movement function using loudest sound plus snr.
import numpy as np


def decide_next_direction(self, detected_sound_objects):
    """decide next direction of bat based on sound

    Args:
        detected_sound_objects (list): list containing detected sounds
    """
    effect_strength = np.pi
    spl_threshold_for_attractions = self.parameters_df["SPL_THRESHOLD_FOR_ATTRACTION"][
        0
    ]
    spl_threshold_for_repulsions = self.parameters_df["SPL_THRESHOLD_FOR_REPULSION"][0]
    if len(detected_sound_objects) != 0:
        max_spl = np.max([i["received_spl"] for i in detected_sound_objects])

        if max_spl > spl_threshold_for_attractions:

            max_spl_sound = [
                i for i in detected_sound_objects if i["received_spl"] == max_spl
            ][0]

            max_spl_sound_vector = self.generate_direction_vector_given_sound(
                max_spl_sound
            )

            if max_spl > spl_threshold_for_repulsions:
                next_direction = max_spl_sound_vector.rotate(np.pi).normalize()
                effect_strength = ((max_spl - spl_threshold_for_repulsions) / 5) * np.pi
                # print(f"Repulsion: {max_spl} dB")

            else:
                next_direction = max_spl_sound_vector.normalize()
                effect_strength = (
                    (max_spl - spl_threshold_for_attractions) / 5
                ) * np.pi
                # print(f"Attraction: {max_spl} dB")

        else:
            # Random direction change occasionally
            next_direction = self.generate_random_direction()

    else:
        # Random direction change occasionally
        next_direction = self.generate_random_direction()

    # put a cap on the max rotation based on spl
    cap_directon_change = effect_strength
    if self.direction.angle_between(next_direction) > cap_directon_change:
        next_direction = self.direction.rotate(cap_directon_change)
    elif self.direction.angle_between(next_direction) < -cap_directon_change:
        next_direction = self.direction.rotate(-cap_directon_change)

    return next_direction
