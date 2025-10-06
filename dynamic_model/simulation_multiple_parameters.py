import glob
import multiprocessing
import os
import time

import pandas as pd
from simulation_and_plotting.simulation import Simulation
from supporting_files.utilities import make_dir


def run_one_instance_of_simulation(
    dir_of_one_param_file, simulation_id, data_storage_dir
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
        + f"/iteration_number_{simulation_id}/"
    )
    make_dir(output_dir)
    print(output_dir)
    sim = Simulation(parameter_df, output_dir)
    sim.run()


def parallel_process_with_pool(param_dir, n_runs, data_storage_dir, max_workers=None):
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
            tasks.append((param_file, iteration, data_storage_dir))

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
    PARAM_DIR = "./dynamic_model/paramsets/effect_of_group_size/store_paramsets/"

    N_RUNS = 1  # Number of iterations per parameter set
    DATA_STORAGE_DIR = "/media/adityamoger/T7 Shield1/consistency_of_calls/no_call_directionality/"  # Base output directory
    # MAX_WORKERS = 4  # Limit number of parallel processes

    # Run parallel processing
    print("Starting parallel processing...")
    parallel_process_with_pool(
        param_dir=PARAM_DIR,
        n_runs=N_RUNS,
        data_storage_dir=DATA_STORAGE_DIR,
        # max_workers=MAX_WORKERS,
    )
