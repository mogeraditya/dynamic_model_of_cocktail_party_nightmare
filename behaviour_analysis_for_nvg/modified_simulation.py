import random
import sys

import pandas as pd

sys.path.append("./dynamic_model/")
from agents.bats import Bat
from agents.obstacles import Obstacle
from agents.sounds import DirectSound
from simulation_and_plotting.simulation import Simulation
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
        obstacle_locations,
    ):
        super().__init__(parameters_df, output_dir)
        self.bats = []
        self.obstacles = []
        num_bats = 1  # len(bat_locations.keys()) %2 # just how the csv is organised
        num_obstacles = len(obstacle_locations["y"])
        self.bats = [
            Bat(self.parameters_df, self.output_dir, store_hearing=False)
            for _ in range(int(num_bats))
        ]
        self.obstacles = [
            Obstacle(
                self.parameters_df,
                (obstacle_locations["x"][i], obstacle_locations["y"][i]),
            )
            for i in range(int(num_obstacles))
        ]
        # for i, obstacle in enumerate(self.obstacles):
        #     self.obstacles[i].position = Vector(

        #     )

        # self.bats = self.bats[0:num_bats]
        # print(self.bats[0].id)
        # for i, bat in enumerate(self.bats):
        #     bat_locations
        initial_release_point = make_vector(initial_release_point)
        self.bats[0].position = initial_release_point
        self.bats[0].direction = Vector(
            random.uniform(-1, 0),
            random.uniform(-1, 1),
        ).normalize()
        # self.bats[0].id = 0


if __name__ == "__main__":

    OUTPUT_DIR = r"./consistency_of_calls_movement_rule_data/2_of_5/"
    PARAMETER_FILE_DIR = r"./dynamic_model/paramsets/common_parameters.csv"
    PARAMETER_DF = load_parameters(PARAMETER_FILE_DIR)
    bat_locations_dir = "./behaviour_analysis_for_nvg/bat_start_positions.csv"
    obstacle_locations_dir = "./behaviour_analysis_for_nvg/chain_positions.csv"

    bat_locations = pd.read_csv(bat_locations_dir)
    obstacle_locations = pd.read_csv(obstacle_locations_dir)

    print(bat_locations.keys())

    sim = Modified_Simulation(
        PARAMETER_DF,
        OUTPUT_DIR,
        (bat_locations["x"][2], bat_locations["y"][2]),
        obstacle_locations,
    )
    sim.run()
