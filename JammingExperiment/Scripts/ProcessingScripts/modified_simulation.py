import random
import sys
import uuid

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append("./dynamic_model/")
sys.path.append("./JammingExperiment/Scripts/ProcessingScripts/")
from agents.bats import Bat
from agents.obstacles import Obstacle
from agents.sounds import DirectSound
from collision_scores import (
    compute_collision_counts_and_length,
    compute_collision_rate,
    individual_collision_rate,
    load_history_dump,
    time_spent_in_collision,
)
from simulation_and_plotting.simulation import Simulation
from simulation_and_plotting.single_bat_plotter import visualize
from supporting_files.utilities import (
    creation_time_calculation,
    load_parameters,
    make_vector,
)
from supporting_files.vectors import Vector

# print(obstacle_locations)
# bat_locations =


class Modified_Simulation(Simulation):
    def __init__(
        self,
        parameters_df,
        output_dir,
        initial_release_point,
        jammer_locations,
    ):
        super().__init__(parameters_df, output_dir)
        self.bats = []
        self.obstacles = []
        num_bats = 1  # len(bat_locations.keys()) %2 # just how the csv is organised

        self.bats = [
            Bat(self.parameters_df, self.output_dir, store_hearing=False)
            for _ in range(int(num_bats))
        ]
        if (jammer_locations) is None:
            self.jammers = []
        else:
            num_jammers = len(jammer_locations["y"])
            self.jammers = [
                Bat(
                    self.parameters_df,
                    self.output_dir,
                    store_hearing=False,
                )
                for i in range(int(num_jammers))
            ]
        for i, bat in enumerate(self.jammers):
            bat.kill_movement = True
            bat.position = Vector(jammer_locations["x"][i], jammer_locations["y"][i])
            bat.is_bat_reflective_to_sound = False
        # for i, obstacle in enumerate(self.obstacles):
        #     self.obstacles[i].position = Vector(

        #     )

        # self.bats = self.bats[0:num_bats]
        # print(self.bats[0].id)
        # for i, bat in enumerate(self.bats):
        #     bat_locations
        initial_release_point = make_vector(initial_release_point)
        self.bats[0].position = initial_release_point
        # self.bats[0].direction = Vector(
        #     random.uniform(0, 0),
        #     random.uniform(1, 1),
        # ).normalize()
        self.bats[0].id = 0
        self.bats.extend(self.jammers)


if __name__ == "__main__":
    df_to_store_collsion = pd.DataFrame()
    df_to_store_collsion["jammer_resolution"] = []
    df_to_store_collsion["metric"] = []
    df_to_store_collsion["value"] = []

    store_jammer_resolution = []
    store_metric = []
    store_value = []

    jammer_resolutions = list(np.arange(2, 4, 2))
    for jammer_resolution in jammer_resolutions:
        OUTPUT_DIR = (
            f"./JammingExperiment/Data/IntermediateData/profiling_{jammer_resolution}/"
        )
        PARAMETER_FILE_DIR = r"./JammingExperiment/Data/InputData/common_parameters.csv"

        PARAMETER_DF = load_parameters(PARAMETER_FILE_DIR)
        bat_locations_dir = "./JammingExperiment/Data/InputData/bat_start_positions.csv"
        bat_locations = pd.read_csv(bat_locations_dir)
        # jammer_resolutions = [
        #     0.001,
        #     0.01,
        #     0.1,
        #     1,
        # ]
        if jammer_resolution == 0:
            jammer_locations = None
        else:
            width_array = np.linspace(
                0.5, PARAMETER_DF["ARENA_WIDTH"][0] - 0.5, num=jammer_resolution
            )
            height_array = np.linspace(
                0.5, PARAMETER_DF["ARENA_HEIGHT"][0] - 0.5, num=jammer_resolution
            )
            left_wall = [(0.01, i) for i in height_array]
            right_wall = [
                (PARAMETER_DF["ARENA_WIDTH"][0] - 0.01, i) for i in height_array
            ]
            top_wall = [
                (i, PARAMETER_DF["ARENA_HEIGHT"][0] - 0.01) for i in width_array
            ]
            bottom_wall = [(i, 0.01) for i in width_array]

            positions_to_put_objects = np.array(
                [*left_wall, *right_wall, *top_wall, *bottom_wall]
            )

            jammer_locations = {
                "x": positions_to_put_objects[:, 0],
                "y": positions_to_put_objects[:, 1],
            }
        print(jammer_locations)
        print(bat_locations.keys())
        LOCATION_NUMBER = 0
        chosen_start_location = (
            PARAMETER_DF["ARENA_WIDTH"][0] / 2,
            PARAMETER_DF["ARENA_HEIGHT"][0] / 2,
        )
        sim_identifier = uuid.uuid4()
        sim = Modified_Simulation(
            PARAMETER_DF, OUTPUT_DIR, chosen_start_location, jammer_locations
        )
        sim.run()
        SAVE_ANIMATION = False  # OUTPUT_DIR
        visualize(OUTPUT_DIR, SAVE_ANIMATION, sim_identifier)
        plt.close()
        positions_array = load_history_dump(OUTPUT_DIR + "/data_for_plotting/")
        print(
            f"collision counts : {compute_collision_counts_and_length(positions_array)}"
        )
        print(f"collision rate : {compute_collision_rate(positions_array)}")
        print(f"duration (frames) : {len(positions_array)}")

        store_jammer_resolution.append(jammer_resolution)
        store_metric.append("collision_rate")
        store_value.append(compute_collision_rate(positions_array))

        store_jammer_resolution.append(jammer_resolution)
        store_metric.append("collision_counts")
        store_value.append(compute_collision_counts_and_length(positions_array))

        # store_jammer_resolution.append(jammer_resolution)
        # store_metric.append("collision_time")
        # store_value.append(time_spent_in_collision(positions_array))
        # print(df_to_store_collsion)
        # print(store_value)
    df_to_store_collsion["jammer_resolution"] = store_jammer_resolution
    df_to_store_collsion["metric"] = store_metric
    df_to_store_collsion["value"] = store_value
    df_to_store_collsion.to_csv("loud_nonrandom_data.csv")
