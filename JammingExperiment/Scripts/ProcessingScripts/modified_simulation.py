import random
import sys
import uuid

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append("./dynamic_model/")
sys.path.append("./JammingExperiment/Scripts/ProcessingScripts/")
from agents.class_bats import Bat
from agents.class_jammers import Jammers
from plotting.single_bat_plotter import visualize
from scores.collision_scores import (
    compute_collision_counts_and_length,
    compute_collision_rate,
)
from scores.run_all_score_calculations import (
    filter_bat_positions_from_history,
    load_history_dump,
)
from scores.space_occupied_scores import space_occupied_score
from simulation.class_simulation import Simulation
from supporting_files.utilities import load_parameters, make_vector
from supporting_files.vectors import Vector


class Modified_Simulation(Simulation):
    def __init__(
        self,
        parameters_df,
        output_dir,
        initial_release_point,
        jammer_locations_and_directions,
    ):
        super().__init__(parameters_df, output_dir)
        self.bats = []

        num_bats = 1  # len(bat_locations.keys()) %2 # just how the csv is organised

        self.bats = [
            Bat(self.parameters_df, self.output_dir) for _ in range(int(num_bats))
        ]
        self.jammers = []
        if (jammer_locations_and_directions) is not None:
            num_jammers = len(jammer_locations_and_directions["y"])

            for i in range(num_jammers):
                position = Vector(
                    jammer_locations_and_directions["x"][i],
                    jammer_locations_and_directions["y"][i],
                )
                direction = Vector(
                    jammer_locations_and_directions["direction_x"][i],
                    jammer_locations_and_directions["direction_y"][i],
                )
                jammer_call_rate = 10
                self.jammers.append(
                    Jammers(
                        self.parameters_df,
                        position,
                        direction,
                        jammer_call_rate,
                        wall_id=jammer_locations_and_directions["wall_id"][i],
                    )
                )

        initial_release_point = make_vector(initial_release_point)
        self.bats[0].position = initial_release_point
        self.bats[0].direction = Vector(0, 1)
        self.bats[0].id = 0

    def convert_necessary_information_into_dict(self):
        dictionary_w_information = {
            "time": np.round(self.time_elapsed, self.rounding_based_on_time_step),
            "bat_call_time": [bat.emit_times[-1] for bat in self.bats],
            "bat_positions": [(bat.position.x, bat.position.y) for bat in self.bats],
        }

        return dictionary_w_information


if __name__ == "__main__":
    df_to_store_collsion = pd.DataFrame()
    df_to_store_collsion["jammer_resolution"] = []
    df_to_store_collsion["metric"] = []
    df_to_store_collsion["value"] = []

    store_jammer_resolution = []
    store_metric = []
    store_value = []

    jammer_resolutions = [uuid.uuid4()]
    params = [1.5, 3, 6]
    for param in params:
        for jammer_resolution in jammer_resolutions:
            OUTPUT_DIR = f"./JammingExperiment/Data/IntermediateData/debug11/"

            PARAMETER_FILE_DIR = (
                r"./JammingExperiment/Data/InputData/common_parameters.json"
            )

            PARAMETER_DF = load_parameters(PARAMETER_FILE_DIR)
            PARAMETER_DF["BAT_ROTATION_SPEED"] = [param]
            bat_locations_dir = (
                "./JammingExperiment/Data/InputData/bat_start_positions.csv"
            )
            bat_locations = pd.read_csv(bat_locations_dir)
            jammer_locations = pd.read_csv(
                "./JammingExperiment/Data/InputData/jammer_locations.csv"
            )
            chosen_start_location = (
                PARAMETER_DF["ARENA_WIDTH"][0] / 2,
                PARAMETER_DF["ARENA_LENGTH"][0] / 2,
            )
            sim_identifier = uuid.uuid4()
            sim = Modified_Simulation(
                PARAMETER_DF,
                OUTPUT_DIR,
                chosen_start_location,
                jammer_locations,
            )
            sim.run()
            SAVE_ANIMATION = OUTPUT_DIR
            # visualize(
            #     OUTPUT_DIR,
            #     SAVE_ANIMATION,
            #     sim_identifier,
            #     resolution=30,
            #     show_sounds=False,
            # )
            # plt.close()
            positions_array = filter_bat_positions_from_history(sim.history)
            print(
                f"collision counts : {compute_collision_counts_and_length(positions_array, PARAMETER_DF)}"
            )
            print(
                f"collision rate : {compute_collision_rate(positions_array, PARAMETER_DF)}"
            )
            print(
                f"space ocuupied : {space_occupied_score(PARAMETER_DF, positions_array)}"
            )
            print(f"duration (frames) : {len(positions_array)}")

            store_jammer_resolution.append(jammer_resolution)
            store_metric.append("collision_rate")
            store_value.append(compute_collision_rate(positions_array, PARAMETER_DF))

            store_jammer_resolution.append(jammer_resolution)
            store_metric.append("collision_counts")
            store_value.append(
                compute_collision_counts_and_length(positions_array, PARAMETER_DF)
            )
    df_to_store_collsion["jammer_resolution"] = store_jammer_resolution
    df_to_store_collsion["metric"] = store_metric
    df_to_store_collsion["value"] = store_value
    df_to_store_collsion.to_csv("loud_nonrandom_data.csv")
