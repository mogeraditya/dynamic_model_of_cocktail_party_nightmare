import random
import sys

import pandas as pd

sys.path.append("./dynamic_model/")
from agents.bats import Bat
from agents.obstacles import Obstacle
from agents.sounds import DirectSound
# from  import Bat
from supporting_files.utilities import (
    creation_time_calculation,
    load_parameters,
    make_vector,
)
from supporting_files.vectors import Vector

# print(obstacle_locations)
# bat_locations =


class Modified_Bat(Bat):
    def __init__(
        self,
        parameters_df,
        output_dir,
        store_hearing=False
    ):  
        super().__init__(parameters_df, output_dir, store_hearing)
        
        