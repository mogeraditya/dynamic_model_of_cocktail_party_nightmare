# place holder file that runs simulation for multiple different parameters
import csv
import os
import pickle
import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from agents.bats import Bat
from agents.obstacles import Obstacle
from agents.sounds import DirectSound, EchoSound
from plotter import *
from supporting_files.utilities import load_parameters
from supporting_files.vectors import Vector

plt.rcParams["animation.ffmpeg_path"] = "/usr/bin/ffmpeg"


class Simulation:
    """one instance of the simulation;
    this objects goal is to run the simulation for one
    instance of the set of parameters chosen
    """

    def __init__(self, parameter_file_dir, output_dir, visualize):
        parameters_df = load_parameters(parameter_file_dir)

        self.parameters_df = parameters_df
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # print(self.parameters_df.keys())
        # print(self.parameters_df["ARENA_WIDTH"][0])
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
        if visualize:
            (
                self.fig,
                self.ax,
                self.bat_markers,
                self.sound_artists,
                self.detection_artists,
            ) = setup_visualization(self.parameters_df, self.obstacles, self.bats)
        self.handles = []

    # TODO: make a different module for plotting; disconnect it from simulation

    def run(self):
        num_steps = int(
            self.parameters_df["SIM_DURATION"][0] / self.parameters_df["TIME_STEP"][0]
        )
        start_timing = datetime.now()
        list_time_taken_for_each_loop = []
        save_time_of_last_iter = start_timing
        for step in range(num_steps):
            self.time_elapsed = step * self.parameters_df["TIME_STEP"][0]

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
                        self._serialize_sound(s)
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
        print(f"total_time_taken_to_store_info: {save_time_of_last_iter-start_timing}")
        print(f"average_time_per_loop {np.mean(list_time_taken_for_each_loop)}")
        self.save_simulation_data()
        print("DATA SAVED")
        visualize(
            self.parameters_df,
            self.history,
            self.output_dir,
            fig,
            ax,
            bat_markers,
            sound_artists,
            detection_artists,
        )

    # TODO: add handle reflections somewhere else ig?; disconnect it from simulation; but its okay if this is the
    #
    def handle_reflections(self, current_time):
        new_echoes = []

        for sound in self.sound_objects:
            if not sound.active or not isinstance(
                sound, DirectSound
            ):  # or sound.has_reflected :
                continue

            sound.update(current_time)
            reflection_point = None
            normal = None
            obstacle_id = None

            reflection_point_arr, normal_arr, obstacle_id_arr = [], [], []

            # Check obstacles
            for obstacle in self.obstacles:
                if (
                    sound.contains_point(obstacle.position)
                    and id(obstacle) not in sound.reflected_obstacles
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
                    and id(bat) not in sound.reflected_obstacles
                ):
                    normal = (sound.origin - bat.position).normalize()
                    reflection_point = bat.position + normal * 0.1
                    obstacle_id = f"bat_{bat.id}"

                    normal_arr.append(normal)
                    reflection_point_arr.append(reflection_point)
                    obstacle_id_arr.append(obstacle_id)

                    # break

            for i, arr in enumerate(reflection_point_arr):
                reflection_point = reflection_point_arr[i]
                normal = normal_arr[i]
                obstacle_id = obstacle_id_arr[i]
                if reflection_point and normal and obstacle_id:
                    echo = sound.create_echo(
                        reflection_point, current_time, normal, obstacle_id
                    )
                    # print(echo)
                    if echo:
                        # Mark this obstacle as reflected for the original sound
                        sound.reflected_obstacles.add(obstacle_id)
                        # Copy reflected obstacles to the echo
                        echo.reflected_obstacles.update(sound.reflected_obstacles)
                        new_echoes.append(echo)

        self.sound_objects.extend(new_echoes)

    def _serialize_sound(self, sound):
        # if not isinstance(sound, EchoSound):
        #     print(sound); print(isinstance(sound, DirectSound))
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

    def save_simulation_data(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create a proper dictionary of constants
        # constants_dict = {
        #     'ARENA_WIDTH': self.parameters_df["ARENA_WIDTH"][0],
        #     'ARENA_HEIGHT': self.parameters_df["ARENA_HEIGHT"][0],
        #     'SOUND_SPEED': Constants.SOUND_SPEED,
        #     'BAT_SPEED': Constants.BAT_SPEED,
        #     'SIM_DURATION': Constants.SIM_DURATION,
        #     'TIME_STEP': Constants.TIME_STEP,
        #     'CALL_DURATION': Constants.CALL_DURATION,
        #     'CALL_RATE': Constants.CALL_RATE,
        #     'OBSTACLE_COUNT': Constants.OBSTACLE_COUNT,
        #     'OBSTACLE_RADIUS': Constants.OBSTACLE_RADIUS,
        #     'EMITTED_SPL': Constants.EMITTED_SPL,
        #     'MIN_DETECTABLE_SPL': Constants.MIN_DETECTABLE_SPL,
        #     'NUM_BATS': Constants.NUM_BATS,
        #     'AIR_ABSORPTION': Constants.AIR_ABSORPTION,
        #     'REFLECTION_LOSS': Constants.REFLECTION_LOSS,
        #     'SOUND_DISK_WIDTH': Constants.SOUND_DISK_WIDTH,

        #     'timestamp': timestamp
        # }
        constants_df = self.parameters_df
        constants_df["timestamp"] = timestamp
        simulation_data = {
            "parameters": constants_df,  # Use the plain dictionary
            "bat_data": [],
            "obstacle_positions": [
                (o.position.x, o.position.y) for o in self.obstacles
            ],
            "sound_history": self.history,
        }

        for bat in self.bats:
            bat_data = {
                "id": bat.id,
                "position_history": bat.position_history,
                "received_sounds": bat.received_sounds,
                "emitted_sounds": [
                    {
                        "creation_time": s.creation_time,
                        "origin": (s.origin.x, s.origin.y),
                        "initial_spl": s.initial_spl,
                    }
                    for s in bat.emitted_sounds
                ],
            }
            simulation_data["bat_data"].append(bat_data)

        filename = f"bat_simulation_{timestamp}.pkl"
        filepath = os.path.join(self.output_dir, filename)

        # with open(filepath, 'wb') as f:
        #     pickle.dump(simulation_data, f)

        # with open("mycsvfile.csv", "w", newline="") as f:
        #     w = csv.DictWriter(f, constants_df.keys())
        #     w.writeheader()
        #     w.writerow(constants_df)
        #     print(f"Saved simulation data to {filepath}")

    # TODO: make a different module for plotting; disconnect it from simulation
    #


print(os.getcwd())
output_dir = "test_storage"
parameter_file_dir = r"./dynamic_model/paramsets/intensive_test.csv"
if __name__ == "__main__":
    sim = Simulation(parameter_file_dir, output_dir)
    sim.run()
