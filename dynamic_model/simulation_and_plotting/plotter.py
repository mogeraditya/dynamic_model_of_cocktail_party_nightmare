import glob
import os
import pickle
import sys

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Arrow, Circle, Patch, Rectangle, Wedge

sys.path.append("./dynamic_model")
plt.rcParams["animation.ffmpeg_path"] = "/usr/bin/ffmpeg"


def stitch_together_history_lists(history_output_dir):
    """Merges lists from all the pickle files together.

    Args:
        history_output_dir (string):

    Returns:
        list: list with all the merged lists from pickle files.
    """
    list_of_dict_files = glob.glob(history_output_dir + "/history_dump_*.pkl")
    list_of_dict_files = np.sort(list_of_dict_files)
    list_containing_data_from_all_pickle_files = []
    for pickle_file in list_of_dict_files:
        with open(pickle_file, "rb") as f:
            _list_containing_subset = pickle.load(f)
            list_containing_data_from_all_pickle_files.extend(_list_containing_subset)

    parameter_file = glob.glob(history_output_dir + "/parameters_used.pkl")[0]
    parameter_df = pd.read_pickle(parameter_file)
    with open(history_output_dir + "/bats_initial.pkl", "rb") as f:
        bats_initial_positions = pickle.load(f)
    with open(history_output_dir + "/obstacles_initial.pkl", "rb") as f:
        obstacles_initial_positions = pickle.load(f)
    return (
        list_containing_data_from_all_pickle_files,
        parameter_df,
        bats_initial_positions,
        obstacles_initial_positions,
    )


def setup_visualization(parameters_df, bats, obstacles):
    """Sets up the figure for animation.

    Args:
        parameters_df (DataFrame): parameters used to run the simulation
        bats (list): bat objects that the simulation was intiated with
        obstacles (list): obstacles objects that the simualtion was intiated with

    Returns:
        list: contains axes, figure, markers and artists to build the animation on.
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, parameters_df["ARENA_WIDTH"][0])
    ax.set_ylim(0, parameters_df["ARENA_HEIGHT"][0])
    ax.set_aspect("equal")
    ax.set_title("Bat Echolocation with Direct Calls and Echoes")

    boundary = Rectangle(
        (0, 0),
        parameters_df["ARENA_WIDTH"][0],
        parameters_df["ARENA_HEIGHT"][0],
        fill=False,
        linestyle="--",
        color="gray",
    )
    ax.add_patch(boundary)

    obstacle_patches = []
    for obstacle in obstacles:
        obs_circle = Circle(
            (obstacle.position.x, obstacle.position.y),
            obstacle.radius,
            color="red",
            alpha=0.5,
        )  # , label=f"Obstacle {obstacle.id}")
        ax.add_patch(obs_circle)
        obstacle_patches.append(obs_circle)

    bat_markers = []
    direction_arrows = []
    sound_artists = []
    detection_artists = []
    trajectory_lines = []

    colors = plt.cm.tab10.colors
    for i, bat in enumerate(bats):

        # trajectory line place holders
        (trajectory_line,) = ax.plot(
            [],
            [],
            color=colors[i % len(colors)],
            linestyle="--",
            alpha=1,
            linewidth=1.5,
        )
        trajectory_lines.append(trajectory_line)

        # bat object placeholders
        bat_circle = Circle(
            (bat.position.x, bat.position.y),
            bat.radius,
            color=colors[i % len(colors)],
            label=f"Bat {bat.id}",
            # alpha=0.5,
        )  # , label=f"Obstacle {obstacle.id}")
        ax.add_patch(bat_circle)

        # (marker,) = ax.plot(
        #     [],
        #     [],
        #     "o",
        #     markersize=10,
        #     color=colors[i % len(colors)],
        #     label=f"Bat {bat.id}",
        # )
        bat_markers.append(bat_circle)

        # direction arrow place holders
        direction_arrow = Arrow(
            bat.position.x,
            bat.position.y,
            0,
            0,  # Initial direction (0, 0)
            width=0.3,  # Adjust arrow width as needed
            color=colors[i % len(colors)],
            alpha=0.8,
        )
        ax.add_patch(direction_arrow)
        direction_arrows.append(direction_arrow)

    return [
        fig,
        ax,
        bat_markers,
        direction_arrows,
        trajectory_lines,
        sound_artists,
        detection_artists,
    ]


def visualize(output_dir, save_animation):
    """Saves animation as an mp4 file and then also plays it.

    Args:
        output_dir (string): the directory of the folder where history pkl files are saved.
    """

    history, parameters_df, bats, obstacles = stitch_together_history_lists(output_dir)
    (
        fig,
        ax,
        bat_markers,
        direction_arrows,
        trajectory_lines,
        sound_artists,
        detection_artists,
    ) = setup_visualization(parameters_df, bats, obstacles)

    # Initialize trajectory history for each bat
    trajectory_history = [[] for _ in range(len(bat_markers))]

    def init():
        for marker in bat_markers:
            marker.center = (np.nan, np.nan)
        for arrow in direction_arrows:
            arrow.set_data(x=np.nan, y=np.nan, dx=0, dy=0)
        for line in trajectory_lines:
            line.set_data([], [])
        return bat_markers + direction_arrows + trajectory_lines

    def animate(i):
        frame = history[i]

        for j, (x, y) in enumerate(frame["bat_positions"]):
            bat_markers[j].center = (x, y)
            if "bat_directions" in frame and j < len(frame["bat_directions"]):
                dx, dy = frame["bat_directions"][j]
                # Scale the direction vector for better visualization
                scale = 0.5  # Adjust this scale factor as needed
                direction_arrows[j].set_data(x=x, y=y, dx=dx * scale, dy=dy * scale)
            trajectory_history[j].append((x, y))

            # Keep only the last 400 positions
            if len(trajectory_history[j]) > 400:
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
        plt.title(f"time step: {i}")

        # colors = plt.cm.tab10.colors
        # for sound in frame["sound_objects"]:
        #     # print(sound)
        #     if not sound["status"]:
        #         continue

        #     emitter_color = colors[sound["emitter_id"] % len(colors)]
        #     alpha = 0.5 - (0.1 * sound.get("reflection_count", 0))

        #     inner = max(0, sound["radius"] - parameters_df["SOUND_DISK_WIDTH"][0])
        #     outer = sound["radius"]

        #     if inner < outer:
        #         if sound["type"] == "direct":
        #             linestyle = "-"
        #             hatching_of_disk = "++"
        #         else:
        #             linestyle = "--"
        #             alpha = 0.5 * alpha
        #             hatching_of_disk = ".."
        #         if inner == 0:
        #             width_of_disk = sound["radius"]
        #         else:
        #             width_of_disk = parameters_df["SOUND_DISK_WIDTH"][0]
        #         wedge = Wedge(
        #             sound["origin"],
        #             outer,
        #             0,
        #             360,
        #             width=width_of_disk,
        #             fill=False,
        #             color=emitter_color,
        #             alpha=alpha,
        #             linestyle=linestyle,
        #             hatch=hatching_of_disk,
        #         )
        #         ax.add_patch(wedge)
        #         sound_artists.append(wedge)

        # for bat_idx, detections in enumerate(frame["bat_detections"]):
        #     for detection in detections:
        #         if detection["type"] == "direct":
        #             color = "green"
        #         else:
        #             color = colors[detection["emitter_id"] % len(colors)]

        #         dx, dy = detection["position"]
        #         marker = Circle((dx, dy), 0.05, color=color, alpha=0.7)
        #         ax.add_patch(marker)
        #         detection_artists.append(marker)

        #         bat_x, bat_y = frame["bat_positions"][bat_idx]
        #         (line,) = ax.plot([bat_x, dx], [bat_y, dy], color=color, alpha=0.2)
        #         detection_artists.append(line)

        return (
            bat_markers
            + direction_arrows
            + trajectory_lines
            + sound_artists
            + detection_artists
        )

    # history, parameters_df, bats, obstacles = stitch_together_history_lists(output_dir)
    # (
    #     fig,
    #     ax,
    #     bat_markers,
    #     direction_arrows,
    #     trajectory_lines,
    #     sound_artists,
    #     detection_artists,
    # ) = setup_visualization(parameters_df, bats, obstacles)
    # trajectory_history = [[] for _ in range(len(bats))]
    ani = animation.FuncAnimation(
        fig,
        animate,
        frames=len(history),
        init_func=init,
        blit=False,
        interval=parameters_df["FRAME_RATE"][0] * 0.00001,
    )

    handles, labels = ax.get_legend_handles_labels()
    print(labels)
    obstacle_patch = Patch(color="red", alpha=0.5, label="Obstacle")
    directsound_patch = Patch(hatch="++", label="DirectSound")
    echosound_patch = Patch(hatch="..", label="EchoSound")

    handles.append(directsound_patch)
    handles.append(echosound_patch)
    handles.append(obstacle_patch)
    # DirectSound_patch = Patch(hatch="++", label='DirectSound')
    # plt.legend()
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), handles=handles)
    if save_animation:
        ffwriter = animation.FFMpegWriter(fps=parameters_df["FRAME_RATE"][0])
        ani.save(
            save_animation + "/animation_with_sound.mp4",
            writer=ffwriter,
        )
    plt.show()


if __name__ == "__main__":
    print(os.getcwd())
    OUTPUT_DIR = (
        r"./test_intelligent_movement_2bats_nice_rotations_capped/data_for_plotting/"
    )
    SAVE_ANIMATION = False  # OUTPUT_DIR
    visualize(OUTPUT_DIR, SAVE_ANIMATION)
    # history, parameters_df, bats, obstacles = stitch_together_history_lists(OUTPUT_DIR)
    # next_dir_data = [np.degrees(i["next_dir_angle"][0]) for i in history]
    # dir_data = [np.degrees(i["current_dir_angle"][0]) for i in history]
    # plt.plot(next_dir_data)
    # plt.plot(dir_data)
    # plt.show()

# x = Circle((0, 0), 1)
# print(x)
# x.center = (, )
# print(x)
