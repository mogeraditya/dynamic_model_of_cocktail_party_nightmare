import random

import numpy as np
from agents.class_sounds import DirectSound


class Jammers:
    _id_counter = 0

    def __init__(self, parameters_df, position, direction, call_rate, wall_id=None):
        self.id = Jammers._id_counter
        Jammers._id_counter += 1

        self.parameters_df = parameters_df
        self.position = position
        self.direction = direction.normalize()
        self.radius = 0.125

        time_step_size = self.parameters_df["TIME_STEP"]
        # find the number of decimal places to set rounding equal to time step size
        self.rounding_based_on_time_step = len(str(time_step_size).split(".")[1])

        self.time_since_last_call = -np.inf
        self.call_rate = call_rate
        self.time_since_last_call = np.round(
            random.uniform(0, 1 / self.call_rate),
            self.rounding_based_on_time_step,
        )
        self.emit_times = []

        # TODO : special directivity for jammer speakers.
        # TODO : think about wall reflection implementation.

        self.wall_id = wall_id if wall_id is not None else None

    def update(self, current_time, sound_objects):
        """Function to update jammerss with time.
        This function handles sound emission.

        Args:
            current_time (float): Time, in seconds, for which the simualtion has been running.
            sound_objects (EchoSound): direct and echo sounds that are currently active.
        """

        self.emit_sounds(current_time, sound_objects)

    def emit_sounds(self, current_time, sound_objects):
        """Trigger sound emission by Jammer.
        Whenever the function is called, it checks if sufficient time
        has passed and a DirectSoundObject is created.

        Args:
            current_time (float): Time, in seconds, for which the simualtion has been running.
            sound_objects (list): List containing all active sounds in the simulation
        """
        self.time_since_last_call += self.parameters_df["TIME_STEP"]
        call_interval = 1.0 / self.call_rate

        if self.time_since_last_call >= call_interval:
            sound = DirectSound(
                parameters_df=self.parameters_df,
                origin=self.position,
                creation_time=current_time,
                emitter_id=self.id,
                direction_vector=self.direction,
            )
            sound.wall_id = self.wall_id
            self.emit_times.append(current_time)
            sound_objects.append(sound)

            self.time_since_last_call = np.random.uniform(
                -self.parameters_df["NOISE_IN_CALL_RATE"],
                self.parameters_df["NOISE_IN_CALL_RATE"],
            )

    def __repr__(self):
        return f"Jammer(id={self.id}, position={self.position}, direction={self.direction})"
