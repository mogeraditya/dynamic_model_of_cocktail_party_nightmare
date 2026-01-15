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

        parameters_df["ARENA_WIDTH"] = [3.9]
        parameters_df["ARENA_LENGTH"] = [2.6]
        parameters_df["SIM_DURATION"] = [10]

        self.bats = []

        num_bats = 1

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
            bat.parameters_df["REFLECTION_LOSS"] = [-np.inf]
            bat.parameters_df["CALL_RATE"] = [0.000001]
            if (
                jammer_locations["speaker_direction_x"][i] == 0
                and jammer_locations["speaker_direction_y"][i] == 0
            ):
                bat.parameters_df["CALL_DIRECTIONALITY"] = [0]
                bat.direction = Vector(0, 1)
            else:
                bat.direction = Vector(
                    jammer_locations["speaker_direction_x"][i],
                    jammer_locations["speaker_direction_y"][i],
                )

        initial_release_point = make_vector(initial_release_point)
        self.bats[0].position = initial_release_point
        self.bats[0].direction = Vector(1, 0)
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

    JAMMER_LOCATIONS_DIR = "./JammingExperiment/Data/InputData/jammer_positions.csv"
    JAMMER_LOCATIONS = pd.read_csv(JAMMER_LOCATIONS_DIR)

    sim_identifier = uuid.uuid4()
    OUTPUT_DIR = (
        f"./JammingExperiment/Data/IntermediateData/simulation_files_{sim_identifier}/"
    )
    PARAMETER_FILE_DIR = r"./JammingExperiment/Data/InputData/common_parameters.json"

    PARAMETER_DF = load_parameters(PARAMETER_FILE_DIR)

    chosen_start_location = (0.8, 0.8)

    sim = Modified_Simulation(
        PARAMETER_DF, OUTPUT_DIR, chosen_start_location, JAMMER_LOCATIONS
    )
    sim.run()
    SAVE_ANIMATION = False  # OUTPUT_DIR
    visualize(OUTPUT_DIR, SAVE_ANIMATION, sim_identifier)
    plt.close()
    positions_array = load_history_dump(OUTPUT_DIR + "/data_for_plotting/")
    print(
        f"collision counts : {compute_collision_counts_and_length(positions_array, PARAMETER_DF)}"
    )
    print(f"collision rate : {compute_collision_rate(positions_array, PARAMETER_DF)}")
    print(f"duration (frames) : {len(positions_array)}")

    store_metric.append("collision_rate")
    store_value.append(compute_collision_rate(positions_array, PARAMETER_DF))

    store_metric.append("collision_counts")
    store_value.append(
        compute_collision_counts_and_length(positions_array, PARAMETER_DF)
    )

    # df_to_store_collsion["jammer_resolution"] = store_jammer_resolution
    df_to_store_collsion["metric"] = store_metric
    df_to_store_collsion["value"] = store_value
    df_to_store_collsion.to_csv(OUTPUT_DIR + "loud_nonrandom_data.csv")
