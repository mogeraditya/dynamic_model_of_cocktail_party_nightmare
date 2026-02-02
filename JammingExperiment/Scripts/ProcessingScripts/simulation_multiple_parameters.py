import glob
import multiprocessing
import os
import sys
import time

sys.path.append("./dynamic_model/")
sys.path.append("./JammingExperiment/Scripts/ProcessingScripts/")
import pandas as pd
from modified_simulation import Modified_Simulation
from scores.run_all_score_calculations import take_history_store_scores
from supporting_files.utilities import load_parameters, make_dir

counter = 0


def run_one_instance_of_simulation(
    dir_of_one_param_file,
    simulation_id,
    data_storage_dir,
    initial_release_point,
):
    """run one instance of the simulation

    Args:
        dir_of_one_param_file (str): directory of one param file
        simulation_id (int): used to track the iteration number of the sim

    """
    # if simulation_id == 0:
    #     raise ValueError
    # else:
    #     counter+=1
    parameter_df = load_parameters(dir_of_one_param_file)
    store_scores = []
    for i in range(100):
        output_dir = (
            data_storage_dir
            + parameter_df["OUTPUT_DIR_FOR_SIMULATION"]
            + f"iteration_number_{simulation_id}{i}"
        )
        make_dir(output_dir)
        sim = Modified_Simulation(
            parameter_df,
            output_dir,
            initial_release_point,
        )
        sim.run()
        sim.save_history_csv()
        store_scores.append(take_history_store_scores(sim, f"iteration_number_{i}"))

    df_hearing_data = pd.DataFrame.from_dict(store_scores)
    df_hearing_data.to_csv(
        data_storage_dir + parameter_df["PARAM_LABEL"] + "_scores.csv"
    )
    return


def parallel_process_with_pool(
    param_dir,
    n_runs,
    data_storage_dir,
    max_workers,
    initial_release_point,
):
    """run simulation multiple times for all parameter files

    Args:
        param_dir (str): directory containing all the parameter files
        n_runs (int): number of iteraitions per parameter file
        max_workers (int, optional): maximum number of cores that need to be used. Defaults to None.
    """
    # Find parameter files
    param_files = glob.glob(os.path.join(param_dir, "*.json"))
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
    PARAM_DIR = "./JammingExperiment/Data/InputData/sensitivity_params/"

    N_RUNS = 1  # Number of iterations per parameter set
    DATA_STORAGE_DIR = r"./sensitivity_analysis/"  # Base output directory
    # MAX_WORKERS = 4  # Limit number of parallel processes

    # Run parallel processing
    print("Starting parallel processing...")

    chosen_start_location = (5, 3.5)
    parallel_process_with_pool(
        param_dir=PARAM_DIR,
        n_runs=N_RUNS,
        data_storage_dir=DATA_STORAGE_DIR,
        max_workers=None,
        initial_release_point=chosen_start_location,
    )
