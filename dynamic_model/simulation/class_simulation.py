"""Contains the code that describes a Simulation object. Runs one instance, given parameters."""

import json
import os
import pickle
import sys
import uuid
from datetime import datetime

import numpy as np
import pandas as pd

# from supporting_files.store_history import CompactHistoryManager

sys.path.append("./dynamic_model/")
from agents.class_bats import Bat
from agents.class_obstacles import Obstacle
from agents.class_sounds import DirectSound
from agents.make_walls import make_walls
from plotting.single_bat_plotter import visualize
from supporting_files.utilities import (
    creation_time_calculation,
    load_parameters,
    read_temporal_masking_fn,
)
from supporting_files.vectors import Vector


class Simulation:
    """one instance of the simulation;
    this object's goal is to run the simulation for one
    instance of the set of parameters chosen
    """

    def __init__(self, parameters_df, output_dir, store_history=True):

        Bat._id_counter = 0
        Obstacle._id_counter = 0
        self.parameters_df = parameters_df
        self.output_dir = output_dir + "/"
        self.dir_to_store = self.output_dir  # + "/data_for_plotting/"

        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.dir_to_store, exist_ok=True)

        self.bats = [
            Bat(self.parameters_df, self.output_dir)
            for _ in range(int(self.parameters_df["NUM_BATS"]))
        ]
        self.bats[0].allocentric_axis_y = Vector(0, 1)
        obstacle_position = "random"
        obstacle_radius = self.parameters_df["OBSTACLE_RADIUS"]
        self.obstacles = [
            Obstacle(self.parameters_df, obstacle_position, obstacle_radius)
            for _ in range(int(self.parameters_df["OBSTACLE_COUNT"]))
        ]
        self.jammers = []
        self.wall_objects = make_walls(self.parameters_df)

        self.sound_objects = []  # Contains both DirectSound and EchoSound

        self.time_elapsed = 0.0
        self.history = []
        time_step_size = self.parameters_df["TIME_STEP"]
        # find the number of decimal places to set rounding equal to time step size
        self.store_history = store_history
        self.rounding_based_on_time_step = len(str(time_step_size).split(".")[1])

    def run(self):
        """Runs one instance of the simulation.
        After parsing the parameter file, it runs one instance of the simulation
        for those sets of parameters.
        """
        with open(self.dir_to_store + "bats_initial.pkl", "wb") as f:
            pickle.dump(self.bats, f)
        with open(self.dir_to_store + "obstacles_initial.pkl", "wb") as f:
            pickle.dump(self.obstacles, f)
        with open(self.dir_to_store + "jammers_initial.pkl", "wb") as f:
            pickle.dump(self.jammers, f)
        temporal_masking_fn_choice = self.parameters_df["TEMPORAL_MASKING_FN_TYPE"]

        if temporal_masking_fn_choice == "chopped":
            temporal_masking_file = read_temporal_masking_fn(
                "./dynamic_model/supporting_files/temporal_masking_fn_chopped.csv"
            )
        elif temporal_masking_fn_choice == "full":
            temporal_masking_file = read_temporal_masking_fn(
                "./dynamic_model/supporting_files/temporal_masking_fn.csv"
            )
        else:
            raise ValueError("unsupported temporal masking fn")

        time_array = np.round(
            np.arange(
                0, self.parameters_df["SIM_DURATION"], self.parameters_df["TIME_STEP"]
            ),
            self.rounding_based_on_time_step,
        )
        # save initial snapshot of the simulation
        self.history.append(self.convert_necessary_information_into_dict())

        start_timing = datetime.now()
        list_time_taken_for_each_loop = []
        save_time_of_last_iter = start_timing

        for time_step in time_array[1:]:
            try:
                self.time_elapsed = time_step

                for sound in self.sound_objects:
                    sound.update(self.time_elapsed)

                for bat in self.bats:
                    bat.update(
                        self.time_elapsed, self.sound_objects, temporal_masking_file
                    )

                for jammer in self.jammers:
                    jammer.update(self.time_elapsed, self.sound_objects)

                self.handle_reflections(self.time_elapsed)

                self.sound_objects = [
                    s
                    for s in self.sound_objects
                    if s.active
                    and s.current_spl > self.parameters_df["HEARING_THRESHOLD"]
                ]

                self.history.append(self.convert_necessary_information_into_dict())
                current_loop_time = datetime.now()
                list_time_taken_for_each_loop.append(
                    current_loop_time - save_time_of_last_iter
                )

                save_time_of_last_iter = current_loop_time

                if self.store_history:
                    # self.handle_data_storage_for_plotting(self.time_elapsed, False)
                    self.handle_data_storage_for_plotting_pickle(
                        self.time_elapsed, False
                    )
            except BaseException:
                print("Unexpected error:", sys.exc_info()[0])
                print(
                    f"error in file {self.parameters_df["OUTPUT_DIR_FOR_SIMULATION"]}"
                )
                break

        if self.store_history:
            # self.handle_data_storage_for_plotting(self.time_elapsed, True)
            self.handle_data_storage_for_plotting_pickle(self.time_elapsed, True)

        print(self.parameters_df["OUTPUT_DIR_FOR_SIMULATION"])
        print(f"total_time_taken_to_store_info: {save_time_of_last_iter-start_timing}")
        print(f"average_time_per_loop {np.mean(list_time_taken_for_each_loop)}")
        if self.store_history:
            print("DATA SAVED")

    def convert_necessary_information_into_dict(self):
        """Handles information storage of simulation.
        Every iteration a subset of the simulation data
        needs to be stored, for later processing.

        Returns:
            dictionary : dictionary containing current simulation data
        """
        dictionary_w_information = {
            "time": np.round(self.time_elapsed, self.rounding_based_on_time_step),
            "bat_ipi_counters": [len(bat.emit_times) for bat in self.bats],
            "bat_call_time": [bat.emit_times[-1] for bat in self.bats],
            "bat_positions": [(bat.position.x, bat.position.y) for bat in self.bats],
            "bat_directions": [
                (bat.direction.normalize().x, bat.direction.normalize().y)
                for bat in self.bats
            ],
            # "sound_objects": [
            #     self.serialize_sound(s)
            #     for s in self.sound_objects
            #     if s.active and s.current_spl > self.parameters_df["HEARING_THRESHOLD"]
            # ],
            "sound_objects_count": len(self.sound_objects),
            "jammer_positions": [
                (jammer.position.x, jammer.position.y) for jammer in self.jammers
            ],
            "jammer_directions": [
                (jammer.direction.x, jammer.direction.y) for jammer in self.jammers
            ],
            "next_dir_angle": [
                bat.next_direction.angle_between(Vector(1, 0)) for bat in self.bats
            ],
            "current_dir_angle": [
                bat.direction.angle_between(Vector(1, 0)) for bat in self.bats
            ],
            "bat_response_vector": [
                (bat.next_direction.x, bat.next_direction.y) for bat in self.bats
            ],
            "response_type": [bat.response_type for bat in self.bats],
            "bat_ipi_matrix": [bat.ipi_matrix for bat in self.bats],
            "bat_sum_matrix": [bat.memory_window_sum_matrix for bat in self.bats],
        }
        return dictionary_w_information

    def handle_data_storage_for_plotting_pickle(self, current_time, is_end_of_code):
        """Generates files for data used for plotting.
        Periodically the history list is cleared to ensure
        RAM doesnt get used up.
        """
        history_array_size_limit = self.parameters_df["CLEANUP_PLOT_DATA"]

        if len(self.history) > history_array_size_limit or is_end_of_code:
            time_stamp = f"{current_time:.4f}".zfill(9)
            with open(self.dir_to_store + f"history_dump_{time_stamp}.pkl", "wb") as f:
                pickle.dump(self.history, f)
            self.history = []

        if is_end_of_code:
            with open(
                self.dir_to_store + "/parameters_used.json", "w", encoding="utf-8"
            ) as fp:
                json.dump(self.parameters_df, fp)
            # self.parameters_df.to_pickle(self.dir_to_store + "/parameters_used.pkl")

    def handle_data_storage_for_plotting(self, current_time, is_end_of_code):
        """Generates files for data used for plotting.
        Periodically the history list is cleared to ensure
        RAM doesnt get used up.
        """
        history_array_size_limit = self.parameters_df["CLEANUP_PLOT_DATA"]

        if len(self.history) > history_array_size_limit or is_end_of_code:
            # Save current batch as compressed numpy file instead of pickle
            filename = self.dir_to_store + f"history_dump_{current_time:.3f}.npz"

            # Convert history to compact numpy format
            times = []
            positions = []

            for frame in self.history:
                times.append(frame["time"])
                frame_positions = []
                for bat_pos in frame["bat_positions"]:
                    frame_positions.extend([bat_pos[0], bat_pos[1]])
                positions.append(frame_positions)

            # Save as compressed numpy
            times_array = np.array(times, dtype="f4")
            max_bats = max(len(frame) // 2 for frame in positions) if positions else 0
            positions_array = np.full(
                (len(positions), max_bats * 2), np.nan, dtype="f4"
            )

            for i, frame in enumerate(positions):
                positions_array[i, : len(frame)] = frame

            np.savez_compressed(filename, times=times_array, positions=positions_array)

            # Clear history
            # self.history = []

        if is_end_of_code:
            with open(
                self.dir_to_store + "/parameters_used.json", "w", encoding="utf-8"
            ) as fp:
                json.dump(self.parameters_df, fp)

    def handle_reflections(self, current_time):
        """Generates reflections of the sound objects.
        Soud objects can reflect off of obstacles and bats
        to generate EchoSound s.

        Args:
            current_time (float): Time, in seconds, for which the simualtion has been running.
        """
        new_echoes = []

        for sound in self.sound_objects:
            if not sound.active or not isinstance(sound, DirectSound):
                continue

            reflection_point = None
            normal = None
            obstacle_id = None

            reflection_point_arr, normal_arr, obstacle_id_arr = [], [], []

            # check walls
            for wall_objects in self.wall_objects:
                # check only for jammer call emissions.

                jammer_wall_check = sound.wall_id != wall_objects.wall_id
                # print(sound, sound.wall_id, wall_objects.wall_id)
                if (
                    sound.contains_point(wall_objects.position)
                    and f"wall_obstacle_{wall_objects.id}"
                    not in sound.reflected_obstacles
                    and jammer_wall_check
                ):
                    normal = wall_objects.get_reflection_normal(sound.origin)
                    reflection_point = (
                        wall_objects.position + normal * wall_objects.radius
                    )
                    obstacle_id = f"wall_obstacle_{wall_objects.id}"

                    normal_arr.append(normal)
                    reflection_point_arr.append(reflection_point)
                    obstacle_id_arr.append(obstacle_id)
            # check obstacles
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

            # check other bats
            for bat in self.bats:
                if (
                    sound.contains_point(bat.position)
                    and sound.emitter_id != bat.id
                    and f"bat_{bat.id}" not in sound.reflected_obstacles
                    and bat.is_bat_reflective_to_sound
                ):
                    normal = (sound.origin - bat.position).normalize()
                    reflection_point = bat.position + normal * bat.radius
                    obstacle_id = f"bat_{bat.id}"

                    normal_arr.append(normal)
                    reflection_point_arr.append(reflection_point)
                    obstacle_id_arr.append(obstacle_id)

            for i, reflection_point in enumerate(reflection_point_arr):
                normal = normal_arr[i]
                obstacle_id = obstacle_id_arr[i]
                if obstacle_id not in sound.reflected_obstacles:
                    time_of_creation = creation_time_calculation(
                        sound, reflection_point
                    )

                    echo = sound.create_echo(
                        reflection_point, time_of_creation, normal, obstacle_id
                    )

                    if echo:
                        # mark this obstacle as reflected for the original sound
                        echo.update(current_time)
                        sound.reflected_obstacles.add(obstacle_id)
                        # copy reflected obstacles to the echo
                        echo.reflected_obstacles.update(sound.reflected_obstacles)
                        new_echoes.append(echo)

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

        return data


if __name__ == "__main__":
    OUTPUT_DIR = r"./MISC/testing_single/thesis_video"
    PARAMETER_FILE_DIR = r"./dynamic_model/paramsets/test_single.json"
    PARAMETER_DF = load_parameters(PARAMETER_FILE_DIR)
    sim = Simulation(PARAMETER_DF, OUTPUT_DIR)
    sim.run()

    unique_id = uuid.uuid4()
    visualize(
        output_dir=OUTPUT_DIR,
        save_animation=True,
        unique_id=unique_id,
        resolution=30,
        show_sounds=False,
    )
    print(unique_id)
