import glob
import multiprocessing
import os
import time

import pandas as pd
from supporting_files.utilities import make_dir

from ChainExperiment.Scripts.ProcessingScripts.modified_simulation import (
    Modified_Simulation,
)


def run_one_instance_of_simulation(
    dir_of_one_param_file,
    simulation_id,
    data_storage_dir,
    initial_release_point,
    obstacle_locations,
):
    """run one instance of the simulation

    Args:
        dir_of_one_param_file (str): directory of one param file
        simulation_id (int): used to track the iteration number of the sim
    """
    parameter_df = pd.read_csv(dir_of_one_param_file)
    output_dir = (
        data_storage_dir
        + parameter_df["OUTPUT_DIR_FOR_SIMULATION"][0]
        + f"iteration_number_{simulation_id}"
    )
    make_dir(output_dir)
    print(output_dir)
    sim = Modified_Simulation(
        parameter_df,
        output_dir,
        initial_release_point,
        obstacle_locations,
    )
    sim.run()


def parallel_process_with_pool(
    param_dir,
    n_runs,
    data_storage_dir,
    max_workers,
    initial_release_point,
    obstacle_locations,
):
    """run simulation multiple times for all parameter files

    Args:
        param_dir (str): directory containing all the parameter files
        n_runs (int): number of iteraitions per parameter file
        max_workers (int, optional): maximum number of cores that need to be used. Defaults to None.
    """
    # Find parameter files
    param_files = glob.glob(os.path.join(param_dir, "*.csv"))
    param_files = [f for f in param_files if os.path.isfile(f)]
    print(param_files)

    if not param_files:
        print(f"No parameter files found in {param_dir}")
        return

    # Prepare tasks
    tasks = []
    for param_file in param_files:
        for iteration in range(n_runs):
            tasks.append(
                (
                    param_file,
                    iteration,
                    data_storage_dir,
                    initial_release_point,
                    obstacle_locations,
                )
            )

    # Process with Pool
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()

    start_time = time.time()

    with multiprocessing.Pool(processes=max_workers) as pool:
        pool.starmap(run_one_instance_of_simulation, tasks)

    end_time = time.time()

    print(f"Pool processing completed in {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    # Directory containing your parameter files
    PARAM_DIR = "./behaviour_analysis_for_nvg/parameters/"

    N_RUNS = 5  # Number of iterations per parameter set
    DATA_STORAGE_DIR = (
        r"/media/adityamoger/T7 Shield/dir_store_snr/"  # Base output directory
    )
    # MAX_WORKERS = 4  # Limit number of parallel processes

    # Run parallel processing
    print("Starting parallel processing...")
    bat_locations_dir = "./behaviour_analysis_for_nvg/bat_start_positions.csv"
    obstacle_locations_dir = "./behaviour_analysis_for_nvg/chain_positions.csv"

    bat_locations = pd.read_csv(bat_locations_dir)
    obstacle_locations = pd.read_csv(obstacle_locations_dir)

    parallel_process_with_pool(
        param_dir=PARAM_DIR,
        n_runs=N_RUNS,
        data_storage_dir=DATA_STORAGE_DIR,
        max_workers=None,
        initial_release_point=(bat_locations["x"][2], bat_locations["y"][2]),
        obstacle_locations=obstacle_locations,
    )
