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
from make_jammer_positions import make_jammers
from plotting.single_bat_plotter import visualize
from scores.collision_scores_single_bat import (
    compute_collision_counts_and_length,
    compute_collision_rate,
)
from scores.run_all_score_calculations import (
    filter_bat_positions_from_history,
    load_history_dump,
    reformat_history,
    take_history_store_scores,
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
    ):
        super().__init__(parameters_df, output_dir, store_history=True)
        self.bats = []

        num_bats = 1  # len(bat_locations.keys()) %2 # just how the csv is organised

        self.bats = [
            Bat(self.parameters_df, self.output_dir) for _ in range(int(num_bats))
        ]

        self.jammers = make_jammers(self.parameters_df)

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
        dictionary_w_information.update(self.parameters_df)
        return dictionary_w_information

    def save_history_csv(self):
        df_position_data = pd.DataFrame.from_dict(self.history, orient="columns")
        df_position_data.to_pickle(self.output_dir + "/full_history.pkl")


if __name__ == "__main__":
    df_to_store_collsion = pd.DataFrame()
    df_to_store_collsion["jammer_resolution"] = []
    df_to_store_collsion["metric"] = []
    df_to_store_collsion["value"] = []

    store_jammer_resolution = []
    store_metric = []
    store_value = []

    params = [180]
    jammer_resolutions = [2]
    for i, param in enumerate(params):
        for jammer_resolution in jammer_resolutions:
            OUTPUT_DIR = "./JammingExperiment/Data/IntermediateData/debug19/"
            PARAMETER_FILE_DIR = (
                # r"./JammingExperiment/Data/InputData/sensitivity_params/paramset_number_0.json"
                r"./JammingExperiment/Data/InputData/common_parameters.json"
            )

            PARAMETER_DF = load_parameters(PARAMETER_FILE_DIR)
            # PARAMETER_DF["SIM_DURATION"] = 5
            # PARAMETER_DF["TIME_DELAY_FOR_DIRECTION_CHANGE"] = 0.006
            # # print(PARAMETER_DF)
            # PARAMETER_DF["BAT_ROTATION_SPEED"] = param

            chosen_start_location = (
                PARAMETER_DF["ARENA_WIDTH"] / 2,
                PARAMETER_DF["ARENA_LENGTH"] / 2,
            )
            sim_identifier = uuid.uuid4()
            sim = Modified_Simulation(
                PARAMETER_DF,
                OUTPUT_DIR,
                chosen_start_location,
            )

            sim.run()
            print(sim.bats)
            print(sim.bats[0].list_to_store_sounds)
            sim.save_history_csv()
            # SAVE_ANIMATION = OUTPUT_DIR
            # visualize(
            #     OUTPUT_DIR,
            #     SAVE_ANIMATION,
            #     sim_identifier,
            #     resolution=30,
            #     show_sounds=False,
            # )
            #             # plt.close()
            positions_array = filter_bat_positions_from_history(sim.history)
            subset_of_focal_bat = reformat_history(
                sim.history, 0, sim.parameters_df, f"iteration_{i}"
            )
            df_position_data = pd.DataFrame.from_dict(
                subset_of_focal_bat, orient="columns"
            )
            print(take_history_store_scores(sim, 0))
            print(
                f"space ocuupied : {space_occupied_score(PARAMETER_DF, positions_array)}"
            )
            print(
                f"collision counts : {compute_collision_counts_and_length(positions_array, PARAMETER_DF)}"
            )
            print(
                f"collision rate : {compute_collision_rate(positions_array, PARAMETER_DF)}"
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
