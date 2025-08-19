"""Contains the code that describes a Simulation object. Runs one instance, given parameters."""

import os
import pickle
from datetime import datetime

import numpy as np
import pandas as pd
from agents.bats import Bat
from agents.obstacles import Obstacle
from agents.sounds import DirectSound
from supporting_files.utilities import creation_time_calculation, load_parameters


class Simulation:
    """one instance of the simulation;
    this object's goal is to run the simulation for one
    instance of the set of parameters chosen
    """

    def __init__(self, parameters_df, output_dir):
        # parameters_df = load_parameters(parameter_file_dir)
        Bat._id_counter = 0
        Obstacle._id_counter = 0
        self.parameters_df = parameters_df
        self.output_dir = output_dir
        self.dir_to_store = self.output_dir + "/data_for_plotting/"

        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.dir_to_store, exist_ok=True)

        self.bats = [
            Bat(self.parameters_df, self.output_dir)
            for _ in range(int(self.parameters_df["NUM_BATS"][0]))
        ]
        self.obstacles = [
            Obstacle(self.parameters_df)
            for _ in range(int(self.parameters_df["OBSTACLE_COUNT"][0]))
        ]
        self.sound_objects = []  # Contains both DirectSound and EchoSound
        self.time_elapsed = 0.0
        self.history = []

        self.handles = []

        with open(self.dir_to_store + "bats_initial.pkl", "wb") as f:
            pickle.dump(self.bats, f)
        with open(self.dir_to_store + "obstacles_initial.pkl", "wb") as f:
            pickle.dump(self.obstacles, f)

    def run(self):
        """Runs one instance of the simulation.
        After parsing the parameter file, it runs one instance of the simulation
        for those sets of parameters.
        """
        num_steps = int(
            self.parameters_df["SIM_DURATION"][0] / self.parameters_df["TIME_STEP"][0]
        )
        start_timing = datetime.now()
        list_time_taken_for_each_loop = []
        save_time_of_last_iter = start_timing
        for step in range(num_steps):
            self.time_elapsed = step * self.parameters_df["TIME_STEP"][0]

            for sound in self.sound_objects:
                sound.update(self.time_elapsed)

            for bat in self.bats:
                bat.update(self.time_elapsed, self.sound_objects)

            self.handle_reflections(self.time_elapsed)

            self.history.append(
                {
                    "time": self.time_elapsed,
                    "bat_positions": [
                        (bat.position.x, bat.position.y) for bat in self.bats
                    ],
                    "bat_detections": [
                        bat.get_detections_at_time(self.time_elapsed)
                        for bat in self.bats
                    ],
                    "sound_objects": [
                        self.serialize_sound(s)
                        for s in self.sound_objects
                        if s.active and s.current_spl > 20
                    ],
                    "sound_objects_count": len(self.sound_objects),
                }
            )

            self.sound_objects = [
                s for s in self.sound_objects if s.active and s.current_spl > 20
            ]

            current_loop_time = datetime.now()
            list_time_taken_for_each_loop.append(
                current_loop_time - save_time_of_last_iter
            )
            # print(current_loop_time-save_time_of_last_iter)
            save_time_of_last_iter = current_loop_time
            self.handle_data_storage_for_plotting(self.time_elapsed, False)
        self.handle_data_storage_for_plotting(self.time_elapsed, True)
        print(f"total_time_taken_to_store_info: {save_time_of_last_iter-start_timing}")
        print(f"average_time_per_loop {np.mean(list_time_taken_for_each_loop)}")
        # self.save_simulation_data()
        print("DATA SAVED")

    def handle_data_storage_for_plotting(self, current_time, is_end_of_code):
        """Generates files for data used for plotting.
        Periodically the history list is cleared to ensure
        RAM doesnt get used up.
        """
        history_array_size_limit = self.parameters_df["CLEANUP_PLOT_DATA"][0]

        # filepath = os.path.join(self.output_dir, _dir_to_save)
        if len(self.history) > history_array_size_limit or is_end_of_code:
            with open(
                self.dir_to_store + f"history_dump_{current_time:.3f}.pkl", "wb"
            ) as f:
                pickle.dump(self.history, f)
            self.history = []

        if is_end_of_code:

            self.parameters_df.to_pickle(self.dir_to_store + "/parameters_used.pkl")
        #     print(f"Saved simulation data to {filepath}")

    def handle_reflections(self, current_time):
        """Generates reflections of the sound objects.
        Soud objects can reflect off of obstacles and bats
        to generate EchoSound s.

        Args:
            current_time (float): Time, in seconds, for which the simualtion has been running.
        """
        new_echoes = []

        for sound in self.sound_objects:
            if not sound.active or not isinstance(
                sound, DirectSound
            ):  # or sound.has_reflected :
                continue

            # sound.update(current_time)
            reflection_point = None
            normal = None
            obstacle_id = None

            reflection_point_arr, normal_arr, obstacle_id_arr = [], [], []

            # Check obstacles
            for obstacle in self.obstacles:
                if (
                    sound.contains_point(obstacle.position)
                    and f"obstacle_{obstacle.id}" not in sound.reflected_obstacles
                ):
                    normal = obstacle.get_reflection_normal(sound.origin)
                    reflection_point = obstacle.position + normal * obstacle.radius
                    obstacle_id = f"obstacle_{obstacle.id}"

                    normal_arr.append(normal)
                    reflection_point_arr.append(reflection_point)
                    obstacle_id_arr.append(obstacle_id)

                    # break

            # Check other bats
            for bat in self.bats:
                if (
                    sound.contains_point(bat.position)
                    and sound.emitter_id != bat.id
                    and f"bat_{bat.id}" not in sound.reflected_obstacles
                ):
                    normal = (sound.origin - bat.position).normalize()
                    reflection_point = bat.position + normal * bat.radius
                    obstacle_id = f"bat_{bat.id}"

                    normal_arr.append(normal)
                    reflection_point_arr.append(reflection_point)
                    obstacle_id_arr.append(obstacle_id)

                    # break

            for i, reflection_point in enumerate(reflection_point_arr):
                normal = normal_arr[i]
                obstacle_id = obstacle_id_arr[i]
                if obstacle_id not in sound.reflected_obstacles:
                    # if reflection_point and normal and obstacle_id:
                    time_of_creation = creation_time_calculation(
                        sound, reflection_point
                    )
                    echo = sound.create_echo(
                        reflection_point, time_of_creation, normal, obstacle_id
                    )
                    # print(echo)
                    if echo:
                        # Mark this obstacle as reflected for the original sound
                        echo.update(current_time)
                        sound.reflected_obstacles.add(obstacle_id)
                        # Copy reflected obstacles to the echo
                        echo.reflected_obstacles.update(sound.reflected_obstacles)
                        new_echoes.append(echo)
        # print(new_echoes)
        self.sound_objects.extend(new_echoes)

    def serialize_sound(self, sound):
        """Serializes sounds into dictionaries.
        This is done for easier storage.

        Args:
            sound (EchoSound): input sound object to be serialized

        Returns:
            dict: data inside the sound obejct is serialized into a dict.
        """
        data = {
            "origin": (sound.origin.x, sound.origin.y),
            "radius": sound.current_radius,
            "spl": sound.current_spl,
            "emitter_id": sound.emitter_id,
            "type": "direct" if isinstance(sound, DirectSound) else "echo",
            "status": sound.active,
        }
        # print(data["type"])
        if not isinstance(sound, DirectSound):
            data.update(
                {
                    "parent_creation_time": sound.parent_creation_time,
                    "reflection_count": sound.reflection_count,
                }
            )

        return data


if __name__ == "__main__":
    OUTPUT_DIR = r"./test_storage_multiple_echoes/"
    PARAMETER_FILE_DIR = r"./dynamic_model/paramsets/paramset_for_trial_run.csv"
    sim = Simulation(PARAMETER_FILE_DIR, OUTPUT_DIR)
    sim.run()
