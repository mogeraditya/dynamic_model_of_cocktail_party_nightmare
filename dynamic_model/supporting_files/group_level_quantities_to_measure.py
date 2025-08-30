import glob
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import scipy as scp
import seaborn as sns
from scipy import stats

sys.path.append("./dynamic_model")
from simulation_and_plotting.plotter import stitch_together_history_lists


# implement collision rate
def compute_collision_rate(history):
    # bat positions
    bat_positions = [i["bat_positions"] for i in history][1000:]
    # compute distance matrix in allf rames
    number_of_collisions_across_time = []
    for position_frame in bat_positions:
        distance_matrix = scp.spatial.distance_matrix(position_frame, position_frame)
        count_collisions = (
            np.sum([distance_matrix < 0.25]) - distance_matrix.shape[0]
        ) / 2
        for bat in position_frame:
            if bat[0] >= 5 or bat[0] <= 0:
                count_collisions += 1
            elif bat[1] >= 7 or bat[1] <= 0:
                count_collisions += 1
        number_of_collisions_across_time.append(count_collisions)

    return np.sum(number_of_collisions_across_time) / len(bat_positions)


def compute_interindividual_distance(history):
    bat_positions = [i["bat_positions"] for i in history][1000:]
    # compute distance matrix in allf rames
    distances_array = []

    for position_frame in bat_positions:
        distance_matrix = scp.spatial.distance_matrix(position_frame, position_frame)
        inter_bat_distances_given_frame = []
        for i in range(distance_matrix.shape[0]):
            for j in range(distance_matrix.shape[0]):
                if i < j:
                    inter_bat_distances_given_frame.append(distance_matrix[i, j])
        distances_array.append(inter_bat_distances_given_frame)

    return distances_array


def plot_data_across_parameters(output_dir):
    folders_in_output_dir = glob.glob(output_dir + "/*")

    dict_w_values = {}
    dict_w_values["collision"] = []
    dict_w_values["parameters"] = []
    dict_w_values["median interindividual dist"] = []
    dict_w_values["mean interindividual dist"] = []
    for i, folder in enumerate(folders_in_output_dir):

        folders_in_parameter = np.sort(glob.glob(folder + "/*"))

        for iteration_folder in folders_in_parameter:
            history, parameters_df = stitch_together_history_lists(
                iteration_folder + "/data_for_plotting/"
            )[0:2]
            dict_w_values["collision"].append(compute_collision_rate(history))
            dict_w_values["parameters"].append(
                parameters_df[parameters_df["VARYING_PARAM"][0]][0]
            )
            interindividual_distance = compute_interindividual_distance(history)
            dict_w_values["mean interindividual dist"].append(
                np.mean(interindividual_distance)
            )
            dict_w_values["median interindividual dist"].append(
                np.median(interindividual_distance)
            )

    return dict_w_values


def rarefaction_curve(output_dir):
    folders = np.sort(glob.glob(output_dir + "/*"))
    store_values = []
    for folder in folders:
        history, parameters_df, bats, obstacles = stitch_together_history_lists(
            folder + "/data_for_plotting/"
        )
        store_values.append(compute_collision_rate(history))
    return store_values
    # x_values_on_curve = np.arange(10, 110, 1)
    # y_values_on_curve_mean = []
    # y_values_on_curve_median = []
    # for x_value in x_values_on_curve:
    #     sub_sample = [
    #         np.mean(np.random.choice(store_values, x_value)) for i in np.arange(50)
    #     ]
    #     y_values_on_curve_mean.append(np.mean(sub_sample))
    #     # y_values_on_curve_median.append(np.median(sub_sample))

    # # plt.plot(x_values_on_curve, y_values_on_curve_median, label="median")
    # plt.plot(x_values_on_curve, y_values_on_curve_mean, label="mean")
    # plt.legend()
    # plt.xlabel("number_of_iterations")
    # plt.ylabel("number_of_collisions")
    # plt.show()


def plot_saturation_analysis(simulation_results, parameter_name):
    """
    Plot saturation analysis for simulation results

    Parameters:
    simulation_results: list or array of results from each simulation run
    parameter_name: name of the parameter for labeling
    """

    n_runs = len(simulation_results)
    cumulative_means = np.cumsum(simulation_results) / np.arange(1, n_runs + 1)

    # Calculate running statistics
    running_means = []
    running_stds = []
    running_ci_lower = []
    running_ci_upper = []

    for i in range(1, n_runs + 1):
        current_data = simulation_results[:i]
        running_means.append(np.mean(current_data))
        running_stds.append(np.std(current_data, ddof=1))

        # Calculate 95% confidence interval
        if i > 1:
            ci = stats.t.interval(
                0.95, i - 1, loc=np.mean(current_data), scale=stats.sem(current_data)
            )
            running_ci_lower.append(ci[0])
            running_ci_upper.append(ci[1])
        else:
            running_ci_lower.append(current_data[0])
            running_ci_upper.append(current_data[0])

    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Plot 1: Running mean with confidence intervals
    ax1.plot(
        range(1, n_runs + 1), running_means, "b-", linewidth=2, label="Running Mean"
    )
    ax1.fill_between(
        range(1, n_runs + 1),
        running_ci_lower,
        running_ci_upper,
        alpha=0.2,
        color="blue",
        label="95% CI",
    )
    ax1.axhline(
        y=running_means[-1],
        color="r",
        linestyle="--",
        label=f"Final Mean: {running_means[-1]:.4f}",
    )
    ax1.set_xlabel("Number of Simulations")
    ax1.set_ylabel(f"Mean {parameter_name}")
    ax1.set_title(f"Saturation Analysis for {parameter_name}")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Relative error and standard error
    relative_errors = [
        abs((mean - running_means[-1]) / running_means[-1]) * 100
        for mean in running_means
    ]
    standard_errors = [std / np.sqrt(i) for i, std in enumerate(running_stds, 1)]

    ax2.plot(range(1, n_runs + 1), relative_errors, "g-", label="Relative Error (%)")
    ax2.plot(
        range(1, n_runs + 1),
        [se * 100 for se in standard_errors],
        "r-",
        label="Standard Error × 100",
    )
    ax2.set_xlabel("Number of Simulations")
    ax2.set_ylabel("Error Metrics")
    ax2.set_title("Convergence Metrics")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    # Print summary statistics
    print(f"Summary Statistics for {parameter_name}:")
    print(f"Final mean: {running_means[-1]:.6f}")
    print(f"Final std: {running_stds[-1]:.6f}")
    print(f"Final standard error: {standard_errors[-1]:.6f}")
    print(f"Final relative error: {relative_errors[-1]:.4f}%")
    print(
        f"95% Confidence Interval: ({running_ci_lower[-1]:.6f}, {running_ci_upper[-1]:.6f})"
    )

    # Check if we've reached convergence
    if relative_errors[-1] < 1.0:  # Less than 1% relative error
        print("Convergence likely achieved (relative error < 1%)")
    else:
        print("May need more simulations for better convergence")


if __name__ == "__main__":
    print(os.getcwd())
    OUTPUT_DIR = r"/home/adityamoger/Documents/GitHub/dynamic_model_of_cocktail_party_nightmare/DATA_effect_time_delay_of_decision/0.01/iteration_number_4/data_for_plotting"  # r"./test_intelligent_movement_25bats_final_epic/data_for_plotting/"
    SAVE_ANIMATION = False  # OUTPUT_DIR
    history, parameters_df, bats, obstacles = stitch_together_history_lists(OUTPUT_DIR)
    # plt.plot(compute_collision_rate(history))
    # plt.show()
    print(compute_collision_rate(history))
    # median_array = np.median(compute_median_interindividual_distance(history), axis=1)
    # plt.plot(median_array)
    # plt.show()
    #
    # plt.boxplot(rarefaction_curve(output_folder))
    # plt.show()
    # output_folder = (
    #     r"dynamic_model/rarefaction/DATA_effect_time_delay_of_decision/0.05/"
    # )
    # values = rarefaction_curve(output_folder)

    # plot_saturation_analysis(values, "collision count/ no. of frames")
    output_folder = r"/home/adityamoger/Documents/GitHub/dynamic_model_of_cocktail_party_nightmare/DATA_effect_time_delay_of_decision/"
    dict_w_values = plot_data_across_parameters(output_folder)

    plt.subplot(1, 3, 1)
    sns.violinplot(data=dict_w_values, x="parameters", y="collision")
    plt.subplot(1, 3, 2)
    sns.violinplot(data=dict_w_values, x="parameters", y="median interindividual dist")
    plt.subplot(1, 3, 3)
    sns.violinplot(data=dict_w_values, x="parameters", y="mean interindividual dist")
    plt.show()
