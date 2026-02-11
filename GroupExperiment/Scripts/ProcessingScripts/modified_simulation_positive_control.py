import sys

sys.path.append("./dynamic_model/")
sys.path.append("./JammingExperiment/Scripts/ProcessingScripts/")
from agents.class_bats import Bat
from class_perfect_hearing_bat import CanOnlyHearSelfEchoBat
from simulation.class_simulation import Simulation


class ModifiedSimulationPositiveControl(Simulation):
    def __init__(
        self,
        parameters_df,
        output_dir,
    ):
        super().__init__(parameters_df, output_dir, store_history=True)
        self.bats = []
        CanOnlyHearSelfEchoBat._id_counter = 0
        Bat._id_counter = 0
        self.bats = [
            CanOnlyHearSelfEchoBat(self.parameters_df, self.output_dir)
            for _ in range(int(self.parameters_df["NUM_BATS"]))
        ]
