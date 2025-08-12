import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Patch, Rectangle, Wedge


def setup_visualization(parameters_df, obstacles, bats):
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
    sound_artists = []
    detection_artists = []

    colors = plt.cm.tab10.colors
    for i, bat in enumerate(bats):
        (marker,) = ax.plot(
            [],
            [],
            "o",
            markersize=10,
            color=colors[i % len(colors)],
            label=f"Bat {bat.id}",
        )
        bat_markers.append(marker)

    return fig, ax, bat_markers, sound_artists, detection_artists


def visualize(
    parameters_df,
    history,
    output_dir,
    fig,
    ax,
    bat_markers,
    sound_artists,
    detection_artists,
):
    def init():
        for marker in bat_markers:
            marker.set_data([], [])
        return bat_markers

    def animate(i):
        frame = history[i]

        for j, (x, y) in enumerate(frame["bat_positions"]):
            bat_markers[j].set_data([x], [y])

        for artist in sound_artists + detection_artists:
            artist.remove()
        sound_artists.clear()
        detection_artists.clear()
        plt.title(f"time step: {i}")
        colors = plt.cm.tab10.colors
        for sound in frame["sound_objects"]:
            # print(sound)
            if not sound["status"]:
                continue

            emitter_color = colors[sound["emitter_id"] % len(colors)]
            alpha = 0.5 - (0.1 * sound.get("reflection_count", 0))

            inner = max(0, sound["radius"] - parameters_df["SOUND_DISK_WIDTH"][0])
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
                    width_of_disk = parameters_df["SOUND_DISK_WIDTH"][0]
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
                ax.add_patch(wedge)
                sound_artists.append(wedge)

        for bat_idx, detections in enumerate(frame["bat_detections"]):
            for detection in detections:
                if detection["type"] == "direct":
                    color = "green"
                else:
                    color = colors[detection["emitter_id"] % len(colors)]

                dx, dy = detection["position"]
                marker = Circle((dx, dy), 0.05, color=color, alpha=0.7)
                ax.add_patch(marker)
                detection_artists.append(marker)

                bat_x, bat_y = frame["bat_positions"][bat_idx]
                (line,) = ax.plot([bat_x, dx], [bat_y, dy], color=color, alpha=0.2)
                detection_artists.append(line)

        return bat_markers + sound_artists + detection_artists

    print("DONE RUNNING THE SIMULATION, NOW RUNNING ANIMATION STORAGE")
    ani = animation.FuncAnimation(
        fig,
        animate,
        frames=len(history),
        init_func=init,
        blit=False,
        interval=parameters_df["FRAME_RATE"][0],
    )

    handles, labels = ax.get_legend_handles_labels()

    Obstacle_patch = Patch(color="red", alpha=0.5, label="Obstacle")
    DirectSound_patch = Patch(hatch="++", label="DirectSound")
    EchoSound_patch = Patch(hatch="..", label="EchoSound")

    handles.append(DirectSound_patch)
    handles.append(EchoSound_patch)
    handles.append(Obstacle_patch)
    # DirectSound_patch = Patch(hatch="++", label='DirectSound')
    # plt.legend()
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), handles=handles)

    FFwriter = animation.FFMpegWriter(fps=parameters_df["FRAME_RATE"])
    ani.save(
        output_dir + f"/animation_w_changed_param_usage_testing_detections.mp4"
    )  # _{ parameters_df['NUM_BATS']}_numobs_{ parameters_df['OBSTACLE_COUNT']}_time_{ parameters_df['SIM_DURATION']}_call_duration_{ parameters_df['CALL_DURATION']}_call_rate_{ parameters_df['CALL_RATE']}_frame_rate_{ parameters_df['FRAME_RATE']}.mp4", writer=FFwriter)
    plt.show()
