import bisect
import glob
import os
import pickle
import sys

import matplotlib as mpl
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Arrow, Circle, Patch, Rectangle, Wedge

sys.path.append("./MISC/analysis_of_data/")
sys.path.append("./MISC/exploratory_analysis/")
sys.path.append("./MISC/dynamic_model/")

from convert_heard_sounds_to_matrix import (
    convert_into_grids,
    convert_into_grids_time_series,
    convert_matrix_for_plotting_nicer,
    generate_heard_sounds_array,
    generate_matrix_array,
)
from read_simulation_output import read_data_per_simulation_per_bat
from snr_implementation import parse_sounds, serialize_sound_info
from supporting_files.supporting_functions_for_consistency import (
    given_parameters_df_return_grid_matrix_zeros,
)
from supporting_files.utilities import load_parameters

plt.style.use("dark_background")
sys.path.append("./dynamic_model")
plt.rcParams["animation.ffmpeg_path"] = (
    r"C:\Users\adity\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"
)
# plt.rcParams["axes.grid"] = True
# plt.rcParams["grid.color"] = "black"
# plt.rcParams["grid.linestyle"] = "--"
# plt.rcParams["grid.linewidth"] = 0.8
# plt.rcParams["axes.labelcolor"] = "black"
# plt.rcParams["axes.titlesize"] = 12
# plt.rcParams["axes.labelsize"] = 10
# plt.rcParams["xtick.color"] = "black"
# plt.rcParams["ytick.color"] = "black"
# plt.rcParams["xtick.labelsize"] = 10
# plt.rcParams["ytick.labelsize"] = 10
# plt.rcParams["text.color"] = "black"


def stitch_together_history_lists(history_output_dir):
    """Merges lists from all the pickle files together.

    Args:
        history_output_dir (string):

    Returns:
        list: list with all the merged lists from pickle files.
    """
    history_output_dir = history_output_dir  # + "/data_for_plotting/"
    list_of_dict_files = glob.glob(history_output_dir + "/history_dump_*.pkl")
    list_of_dict_files = np.sort(list_of_dict_files)

    list_containing_data_from_all_pickle_files = []
    for pickle_file in list_of_dict_files:
        with open(pickle_file, "rb") as f:
            _list_containing_subset = pickle.load(f)
            list_containing_data_from_all_pickle_files.extend(_list_containing_subset)

    parameter_file = glob.glob(history_output_dir + "/parameters_used.json")[0]
    parameter_df = load_parameters(parameter_file)

    with open(history_output_dir + "/bats_initial.pkl", "rb") as f:
        bats_initial_positions = pickle.load(f)
    with open(history_output_dir + "/obstacles_initial.pkl", "rb") as f:
        obstacles_initial_positions = pickle.load(f)
    with open(history_output_dir + "/jammers_initial.pkl", "rb") as f:
        jammers_initial_positions = pickle.load(f)

    times = [i["time"] for i in list_containing_data_from_all_pickle_files]
    sorting_indices = np.argsort(times)
    list_containing_data_from_all_pickle_files = np.array(
        list_containing_data_from_all_pickle_files
    )
    list_containing_data_from_all_pickle_files = (
        list_containing_data_from_all_pickle_files[sorting_indices]
    )

    return (
        list_containing_data_from_all_pickle_files,
        parameter_df,
        bats_initial_positions,
        obstacles_initial_positions,
        jammers_initial_positions,
    )


def plot_grid_matrix_into_radial_time_series(
    grid_matrix, spatial_grid_r, spatial_grid_theta, fig_and_ax, cmin, cmax
):
    r, theta = np.meshgrid(spatial_grid_r, spatial_grid_theta)
    z = grid_matrix.T.copy()
    fig, axs = fig_and_ax

    masked_z = np.ma.masked_where(z == 0, z)

    # Black to Blue to Cyan/Electric Blue
    colors = ["black", "red", "orange", "darkgreen", "green", "lime"]
    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        "black_to_cyan", colors, N=(cmax - cmin + 1)
    )
    cmap.set_bad(color="black", alpha=0)

    im = axs.pcolormesh(theta, r, masked_z, cmap=cmap, shading="auto")
    im.set_clim(cmin, cmax)
    fig.colorbar(im)
    axs.set_thetagrids(range(0, 360, int(360 / 12)))
    axs.set_theta_zero_location("N")

    return im


def setup_visualization(parameters_df, bats, obstacles, jammers):
    """Sets up the figure for animation.

    Args:
        parameters_df (DataFrame): parameters used to run the simulation
        bats (list): bat objects that the simulation was intiated with
        obstacles (list): obstacles objects that the simualtion was intiated with

    Returns:
        list: contains ax[0]es, figure, markers and artists to build the animation on.
    """

    fig, ax = plt.subplots(figsize=(20, 10), nrows=1, ncols=3)
    ax[1].remove()
    ax[2].remove()
    ax[1] = fig.add_subplot(132, projection="polar")
    ax[2] = fig.add_subplot(133, projection="polar")
    print(parameters_df["ARENA_WIDTH"])
    ax[0].set_xlim(0, parameters_df["ARENA_WIDTH"])
    ax[0].set_ylim(0, parameters_df["ARENA_LENGTH"])
    ax[0].set_aspect("equal")
    ax[0].set_title("Bat Echolocation with Direct Calls and Echoes")

    boundary = Rectangle(
        (0, 0),
        parameters_df["ARENA_WIDTH"],
        parameters_df["ARENA_LENGTH"],
        fill=False,
        linestyle="--",
        color="gray",
    )
    ax[0].add_patch(boundary)

    obstacle_patches = []
    for obstacle in obstacles:
        obs_circle = Circle(
            (obstacle.position.x, obstacle.position.y),
            obstacle.radius,
            color="red",
            alpha=0.5,
        )
        ax[0].add_patch(obs_circle)
        obstacle_patches.append(obs_circle)

    jammer_patches = []
    for jammer in jammers:
        direction_arrow = Arrow(
            jammer.position.x,
            jammer.position.y,
            jammer.direction.x,
            jammer.direction.y,  # Initial direction (0, 0)
            width=0.3,  # adjust arrow width as needed here
            color="red",
            alpha=0.8,
        )
        jam_circle = Circle(
            (jammer.position.x, jammer.position.y),
            jammer.radius,
            color="red",
            alpha=0.5,
        )
        ax[0].add_patch(jam_circle)
        ax[0].add_patch(direction_arrow)
        jammer_patches.append(jam_circle)

    bat_markers = []
    direction_arrows = []
    next_direction_arrows = []
    sound_artists = []
    detection_artists = []
    trajectory_lines = []
    num_colors = len(bats)

    cm = plt.get_cmap("gist_rainbow")
    for i, bat in enumerate(bats):

        # trajectory line place holders
        (trajectory_line,) = ax[0].plot(
            [],
            [],
            color="blue",  # cm(i / num_colors),
            linestyle="--",
            alpha=1,
            linewidth=1.5,
        )
        trajectory_lines.append(trajectory_line)

        # bat object placeholders
        bat_circle = Circle(
            (bat.position.x, bat.position.y),
            bat.radius,
            color="blue",  # cm(i / num_colors),
            label=f"Bat {bat.id}",
        )
        ax[0].add_patch(bat_circle)

        bat_markers.append(bat_circle)

        # direction arrow place holders
        direction_arrow = Arrow(
            bat.position.x,
            bat.position.y,
            0,
            0,  # Initial direction (0, 0)
            width=0.3,  # adjust arrow width as needed here
            color="blue",  # cm(i / num_colors),
            alpha=0.8,
        )

        next_direction_arrow = Arrow(
            bat.position.x,
            bat.position.y,
            0,
            0,  # Initial direction (0, 0)
            width=0.3,  # adjust arrow width as needed here
            color="white",
            ec="blue",  # cm(i / num_colors),
            alpha=0.8,
        )

        ax[0].add_patch(direction_arrow)
        direction_arrows.append(direction_arrow)
        ax[0].add_patch(next_direction_arrow)
        next_direction_arrows.append(next_direction_arrow)

    return [
        fig,
        ax,
        bat_markers,
        direction_arrows,
        next_direction_arrows,
        trajectory_lines,
        sound_artists,
        detection_artists,
    ]


def visualize(output_dir, save_animation, unique_id, resolution, show_sounds):
    """Saves animation as an mp4 file and then also plays it.

    Args:
        output_dir (string): the directory of the folder where history pkl files are saved.
    """

    history, parameters_df, bats, obstacles, jammers = stitch_together_history_lists(
        output_dir
    )
    history = history[::resolution]
    (
        fig,
        ax,
        bat_markers,
        direction_arrows,
        next_direction_arrows,
        trajectory_lines,
        sound_artists,
        detection_artists,
    ) = setup_visualization(parameters_df, bats, obstacles, jammers)

    trajectory_history = [[] for _ in range(len(bat_markers))]

    focal_bat = 0
    grid_data_time_series = [frame["bat_ipi_matrix"] for frame in history]
    # print([i[0].shape for i in grid_data_time_series])
    grid_data_time_series_sum = [frame["bat_sum_matrix"] for frame in history]
    rows, columns = given_parameters_df_return_grid_matrix_zeros(parameters_df)[1:3]
    spatial_grid_r = rows

    new_angular_resolution = convert_matrix_for_plotting_nicer(
        grid_data_time_series[0], rows, columns, 10, focal_bat
    )[1]
    new_grid_data_time_series = np.array(
        [
            convert_matrix_for_plotting_nicer(i, rows, columns, 10, focal_bat)[0]
            for i in grid_data_time_series
        ]
    )
    new_grid_data_time_series_sum = np.array(
        [
            convert_matrix_for_plotting_nicer(i, rows, columns, 10, focal_bat)[0]
            for i in grid_data_time_series_sum
        ]
    )

    new_spatial_grid_theta = np.arange(
        -np.pi + new_angular_resolution / 2, np.pi, new_angular_resolution
    )

    ax[1].set_title("sound activations in each ipi")
    ax[2].set_title("responses in 5 ipi")

    ax[1].tick_params("y", rotation=30)
    ax[2].tick_params("y", rotation=30)

    im0 = plot_grid_matrix_into_radial_time_series(
        new_grid_data_time_series[0, 0],
        spatial_grid_r,
        new_spatial_grid_theta,
        fig_and_ax=(fig, ax[1]),
        cmin=0,
        cmax=1,
    )
    im1 = plot_grid_matrix_into_radial_time_series(
        new_grid_data_time_series_sum[0, 0],
        spatial_grid_r,
        new_spatial_grid_theta,
        fig_and_ax=(fig, ax[2]),
        cmin=0,
        cmax=5,
    )

    ipi_counter_plot = plt.figtext(
        0.01,
        0.8,
        f"interpulse interval number : {0}",
        fontsize=25,
        ha="left",
        va="top",
    )
    call_time_plot = plt.figtext(
        0.01,
        0.9,
        f"bat call time : {-np.inf}",
        fontsize=25,
        ha="left",
        va="top",
    )

    def init():
        for marker in bat_markers:
            marker.center = (np.nan, np.nan)
        for arrow in direction_arrows:
            arrow.set_data(x=np.nan, y=np.nan, dx=0, dy=0)
        for arrow in next_direction_arrows:
            arrow.set_data(x=np.nan, y=np.nan, dx=0, dy=0)
        for line in trajectory_lines:
            line.set_data([], [])

        return bat_markers + direction_arrows + trajectory_lines

    def animate(i):
        num_colors = len(bats)
        cm = plt.get_cmap("gist_rainbow")
        frame = history[i]

        for j, (x, y) in enumerate(frame["bat_positions"]):
            bat_markers[j].center = (x, y)
            if "bat_directions" in frame and j < len(frame["bat_directions"]):
                dx, dy = frame["bat_directions"][j]
                # Scale the direction vector for better visualization
                scale = 0.5  # Adjust this scale factor as needed
                direction_arrows[j].set_data(x=x, y=y, dx=dx * scale, dy=dy * scale)
            if "bat_response_vector" in frame and j < len(frame["bat_response_vector"]):
                dx, dy = frame["bat_response_vector"][j]
                # Scale the direction vector for better visualization
                scale = 0.5  # Adjust this scale factor as needed
                if frame["response_type"][j] == "repulsion":
                    # ls = "--"
                    # ec = "red"
                    fcolor = "black"
                elif frame["response_type"][j] == "attraction":
                    fcolor = "white"
                else:
                    fcolor = "grey"
                next_direction_arrows[j].set_data(
                    x=x, y=y, dx=dx * scale, dy=dy * scale
                )
                next_direction_arrows[j].set(fc=fcolor)
            trajectory_history[j].append((x, y))

            # Keep only the last 400 positions
            if len(trajectory_history[j]) > 100:
                trajectory_history[j].pop(0)

            # Update trajectory line
            if len(trajectory_history[j]) > 1:
                x_vals, y_vals = (
                    np.array(trajectory_history[j])[:, 0],
                    np.array(trajectory_history[j])[:, 1],
                )
                trajectory_lines[j].set_data(x_vals, y_vals)

        for artist in sound_artists + detection_artists:
            artist.remove()

        sound_artists.clear()
        detection_artists.clear()
        ax[0].set_title(f"time step: {frame["time"]:.5f}")

        ipi_counter_plot.set_text(
            f"interpulse interval number : {frame["bat_ipi_counters"][focal_bat]}"
        )
        call_time_plot.set_text(f"call time : {frame["bat_call_time"][focal_bat]}")

        im0.set_array(new_grid_data_time_series[i, 0].T)
        im1.set_array(new_grid_data_time_series_sum[i, 0].T)
        if show_sounds:
            for sound in frame["sound_objects"]:
                if not sound["status"]:
                    continue

                emitter_color = cm(sound["emitter_id"] / num_colors)
                alpha = 0.5 - (0.1 * sound.get("reflection_count", 0))

                inner = max(
                    0,
                    sound["radius"]
                    - parameters_df["CALL_DURATION"] * parameters_df["SOUND_SPEED"],
                )
                outer = sound["radius"]

                if inner < outer:
                    if sound["type"] == "direct":
                        linestyle = "-"
                        hatching_of_disk = "++"
                    else:
                        linestyle = "--"
                        alpha = 0.5 * alpha
                        hatching_of_disk = ".."
                    if inner == 0:
                        width_of_disk = sound["radius"]
                    else:
                        width_of_disk = (
                            parameters_df["CALL_DURATION"]
                            * parameters_df["SOUND_SPEED"]
                        )
                    wedge = Wedge(
                        sound["origin"],
                        outer,
                        0,
                        360,
                        width=width_of_disk,
                        fill=False,
                        color=emitter_color,
                        alpha=alpha,
                        linestyle=linestyle,
                        hatch=hatching_of_disk,
                    )
                    ax[0].add_patch(wedge)
                    sound_artists.append(wedge)

        plt.savefig(output_dir + f"/frames/frame_{i}.svg", transparent=True)

        return (
            bat_markers
            + direction_arrows
            # + next_direction_arrows
            + trajectory_lines
            + sound_artists
            + detection_artists
        )

    ani = animation.FuncAnimation(
        fig,
        animate,
        frames=len(history),
        init_func=init,
        blit=False,
        interval=parameters_df["FRAME_RATE"] * 0.00001,
    )
    print(len(history), len(grid_data_time_series))
    handles, labels = ax[0].get_legend_handles_labels()
    print(labels)

    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), handles=handles)
    if save_animation:
        ffwriter = animation.FFMpegWriter(fps=parameters_df["FRAME_RATE"])
        ani.save(
            output_dir + f"/animation_without_sound_id_{unique_id}.mp4",
            writer=ffwriter,
        )
    plt.show()
    # plt.clf()


if __name__ == "__main__":
    print(os.getcwd())
    OUTPUT_DIR = (
        # r"./chain_experiment/3_of_5_position_0/"
        # "/home/adityamoger/Documents/GitHub/dynamic_model_of_cocktail_party_nightmare/MISC/consistency_of_calls_movement_rule_data/presence_revamp_10"
        r"./MISC/testing_single/thesis_video_sensitivity/"
    )
    SAVE_ANIMATION = OUTPUT_DIR
    visualize(OUTPUT_DIR, SAVE_ANIMATION, unique_id=0, resolution=30, show_sounds=False)
