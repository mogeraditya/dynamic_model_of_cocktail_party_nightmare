import glob
from multiprocessing import Pool

import pandas as pd
from simulation import Simulation


def fetch_parameter_file_directories(parameter_dir):
    parameter_files = glob.glob(parameter_dir + "/*.csv")
    return parameter_files


def run_simulations(parameter_dir):
    parameter_files = fetch_parameter_file_directories(parameter_dir)
    for parameter_file in parameter_files:
        parameter_df = pd.read_csv(parameter_file)
        output_dir = parameter_df["OUTPUT_DIR_FOR_SIMULATION"][0]
        sim = Simulation(parameter_df, output_dir)
        sim.run()
