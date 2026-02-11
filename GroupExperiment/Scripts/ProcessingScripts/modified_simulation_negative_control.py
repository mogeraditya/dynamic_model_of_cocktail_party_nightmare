import sys

# import uuid

sys.path.append("./dynamic_model/")
sys.path.append("./JammingExperiment/Scripts/ProcessingScripts/")
from agents.class_bats import Bat
from class_self_deaf_bats import CannotHearSelfEchoBat

# from plotting.single_bat_plotter import visualize
from simulation.class_simulation import Simulation

# from supporting_files.utilities import load_parameters


class ModifiedSimulationNegativeControl(Simulation):
    def __init__(
        self,
        parameters_df,
        output_dir,
    ):
        super().__init__(parameters_df, output_dir, store_history=True)
        self.bats = []
        CannotHearSelfEchoBat._id_counter = 0
        Bat._id_counter = 0
        self.bats = [
            CannotHearSelfEchoBat(self.parameters_df, self.output_dir)
            for _ in range(int(self.parameters_df["NUM_BATS"]))
        ]


# if __name__ == "__main__":
#     OUTPUT_DIR = r"./MISC/testing_groups/um_neg_control_1"
#     PARAMETER_FILE_DIR = r"./dynamic_model/paramsets/test_group.json"
#     PARAMETER_DF = load_parameters(PARAMETER_FILE_DIR)
#     sim = ModifiedSimulationNegativeControl(PARAMETER_DF, OUTPUT_DIR)
#     sim.run()

#     unique_id = uuid.uuid4()
#     visualize(
#         output_dir=OUTPUT_DIR,
#         save_animation=True,
#         unique_id=unique_id,
#         resolution=30,
#         show_sounds=False,
#     )
#     print(unique_id)
