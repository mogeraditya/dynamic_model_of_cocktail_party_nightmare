import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, Rectangle, Wedge, Patch
from supporting_files.constants import Constants
from players.bat import Bat
from players.obstacles import Obstacle
from players.direct_sound import DirectSound
from players.echo_sound import EchoSound
import pickle
import os
from datetime import datetime
import numpy as np
from supporting_files.vectors import Vector

plt.rcParams['animation.ffmpeg_path'] = '/usr/bin/ffmpeg'

class Simulation:
    def __init__(self):
        self.bats = [Bat() for _ in range(Constants.NUM_BATS)]
        self.obstacles = [Obstacle() for _ in range(Constants.OBSTACLE_COUNT)]
        self.sound_objects = []  # Contains both DirectSound and EchoSound
        self.time_elapsed = 0.0
        self.history = []
        self.setup_visualization()
        self.handles= []
        self.output_dir = "simulation_results"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def setup_visualization(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        self.ax.set_xlim(0, Constants.ARENA_WIDTH)
        self.ax.set_ylim(0, Constants.ARENA_HEIGHT)
        self.ax.set_aspect('equal')
        self.ax.set_title('Bat Echolocation with Direct Calls and Echoes')
        
        boundary = Rectangle((0, 0), Constants.ARENA_WIDTH, Constants.ARENA_HEIGHT,
                           fill=False, linestyle='--', color='gray')
        self.ax.add_patch(boundary)
        
        self.obstacle_patches = []
        for obstacle in self.obstacles:
            obs_circle = Circle((obstacle.position.x, obstacle.position.y),
                              obstacle.radius, color='red', alpha=0.5) #, label=f"Obstacle {obstacle.id}")
            self.ax.add_patch(obs_circle)
            self.obstacle_patches.append(obs_circle)
        
        self.bat_markers = []
        self.sound_artists = []
        self.detection_artists = []
        
        colors = plt.cm.tab10.colors
        for i, bat in enumerate(self.bats):
            marker, = self.ax.plot([], [], 'o', markersize=10, 
                                  color=colors[i % len(colors)],
                                  label=f'Bat {bat.id}')
            self.bat_markers.append(marker)
    
        
    
    def run(self):
        num_steps = int(Constants.SIM_DURATION / Constants.TIME_STEP)
        
        for step in range(num_steps):
            self.time_elapsed = step * Constants.TIME_STEP
            
            for bat in self.bats:
                bat.update(Constants.TIME_STEP, self.obstacles, 
                         self.bats, self.time_elapsed, self.sound_objects)
            
            self._handle_reflections(self.time_elapsed)
            
            self.history.append({
                'time': self.time_elapsed,
                'bat_positions': [(bat.position.x, bat.position.y) for bat in self.bats],
                'bat_detections': [bat.get_detections_at_time(self.time_elapsed) for bat in self.bats],
                'sound_objects': [self._serialize_sound(s) for s in self.sound_objects if s.active and s.current_spl>20],
                'sound_objects_count': len(self.sound_objects)
            })
            
            self.sound_objects = [s for s in self.sound_objects if s.active and s.current_spl>20]
        
        self.save_simulation_data()
        self.visualize()
    
    def _handle_reflections(self, current_time):
        new_echoes = []
        # for sound in self.sound_objects:
        #     if not sound.active or isinstance(sound, EchoSound):#or sound.has_reflected :
        #         continue
                
        #     sound.update(current_time)
        #     reflection_point = None
        #     normal = None
        #     obstacle_id = None
            
        #     # Check arena boundaries
        #     sound_edge = sound.origin + Vector2D(sound.current_radius, 0)
        #     if sound_edge.x <= 0:
        #         reflection_point = Vector2D(0, sound.origin.y)
        #         normal = Vector2D(1, 0)
        #         obstacle_id = "left_wall"
        #     elif sound_edge.x >= Constants.ARENA_WIDTH:
        #         reflection_point = Vector2D(Constants.ARENA_WIDTH, sound.origin.y)
        #         normal = Vector2D(-1, 0)
        #         obstacle_id = "right_wall"
        #     elif sound_edge.y <= 0:
        #         reflection_point = Vector2D(sound.origin.x, 0)
        #         normal = Vector2D(0, 1)
        #         obstacle_id = "bottom_wall"
        #     elif sound_edge.y >= Constants.ARENA_HEIGHT:
        #         reflection_point = Vector2D(sound.origin.x, Constants.ARENA_HEIGHT)
        #         normal = Vector2D(0, -1)
        #         obstacle_id = "top_wall"
            
        #     # Check obstacles
        #     for obstacle in self.obstacles:
        #         if (sound.contains_point(obstacle.position) and 
        #             id(obstacle) not in sound.reflected_obstacles):
        #             normal = obstacle.get_reflection_normal(sound.origin)
        #             reflection_point = obstacle.position + normal * obstacle.radius
        #             obstacle_id = id(obstacle)
        #             break
            
        #     # Check other bats
        #     for bat in self.bats:
        #         if (sound.contains_point(bat.position) and 
        #             sound.emitter_id != bat.id and 
        #             id(bat) not in sound.reflected_obstacles):
        #             normal = (sound.origin - bat.position).normalize()
        #             reflection_point = bat.position + normal * 0.1
        #             obstacle_id = id(bat)
        #             break
            
        #     if reflection_point and normal and obstacle_id:
        #         echo = sound.create_echo(reflection_point, current_time, normal)
        #         if echo:
        #             # Mark this obstacle as reflected for the original sound
        #             sound.reflected_obstacles.add(obstacle_id)
        #             # Copy reflected obstacles to the echo
        #             echo.reflected_obstacles.update(sound.reflected_obstacles)
        #             new_echoes.append(echo)
        
        # self.sound_objects.extend(new_echoes)
        for sound in self.sound_objects:
            if not sound.active or isinstance(sound, EchoSound):#or sound.has_reflected :
                continue
                
            sound.update(current_time)
            reflection_point = None
            normal = None
            obstacle_id = None

            reflection_point_arr, normal_arr, obstacle_id_arr = [], [], []
            
            # Check arena boundaries
            # sound_edge = sound.origin - Vector(sound.current_radius, 0)
            # if sound_edge.x <= 0:
            #     reflection_point = Vector(0, sound.origin.y)
            #     normal = Vector(1, 0)
            #     obstacle_id = "left_wall"
            #     normal_arr.append(normal); reflection_point_arr.append(reflection_point); obstacle_id_arr.append(obstacle_id)

            # sound_edge = sound.origin + Vector(sound.current_radius, 0)
            # if sound_edge.x >= Constants.ARENA_WIDTH:
            #     reflection_point = Vector(Constants.ARENA_WIDTH, sound.origin.y)
            #     normal = Vector(-1, 0)
            #     obstacle_id = "right_wall"
            #     normal_arr.append(normal); reflection_point_arr.append(reflection_point); obstacle_id_arr.append(obstacle_id)
            
            # sound_edge = sound.origin - Vector(0, sound.current_radius)
            # if sound_edge.y <= 0:
            #     reflection_point = Vector(sound.origin.x, 0)
            #     normal = Vector(0, 1)
            #     obstacle_id = "bottom_wall"
            #     normal_arr.append(normal); reflection_point_arr.append(reflection_point); obstacle_id_arr.append(obstacle_id)

            # sound_edge = sound.origin + Vector(0, sound.current_radius)
            # if sound_edge.y >= Constants.ARENA_HEIGHT:
            #     reflection_point = Vector(sound.origin.x, Constants.ARENA_HEIGHT)
            #     normal = Vector(0, -1)
            #     obstacle_id = "top_wall"
            #     normal_arr.append(normal); reflection_point_arr.append(reflection_point); obstacle_id_arr.append(obstacle_id)
            
            # Check obstacles
            for obstacle in self.obstacles:
                if (sound.contains_point(obstacle.position) and 
                    id(obstacle) not in sound.reflected_obstacles):
                    normal = obstacle.get_reflection_normal(sound.origin)
                    reflection_point = obstacle.position + normal * obstacle.radius
                    obstacle_id = id(obstacle)

                    normal_arr.append(normal); reflection_point_arr.append(reflection_point); obstacle_id_arr.append(obstacle_id)

                    # break
            
            # Check other bats
            for bat in self.bats:
                if (sound.contains_point(bat.position) and 
                    sound.emitter_id != bat.id and 
                    id(bat) not in sound.reflected_obstacles):
                    normal = (sound.origin - bat.position).normalize()
                    reflection_point = bat.position + normal * 0.1
                    obstacle_id = id(bat)

                    normal_arr.append(normal); reflection_point_arr.append(reflection_point); obstacle_id_arr.append(obstacle_id)                    

                    # break
            
            for i in range(len(reflection_point_arr)):
                reflection_point= reflection_point_arr[i]; normal = normal_arr[i]; obstacle_id= obstacle_id_arr[i]
                if reflection_point and normal and obstacle_id:
                    echo = sound.create_echo(reflection_point, current_time, normal)
                    # print(echo)
                    if echo:
                        # Mark this obstacle as reflected for the original sound
                        sound.reflected_obstacles.add(obstacle_id)
                        # Copy reflected obstacles to the echo
                        echo.reflected_obstacles.update(sound.reflected_obstacles)
                        new_echoes.append(echo)
        
        self.sound_objects.extend(new_echoes)
    
    def _serialize_sound(self, sound):
        # print(sound)
        data = {
            'origin': (sound.origin.x, sound.origin.y),
            'radius': sound.current_radius,
            'spl': sound.current_spl,
            'emitter_id': sound.emitter_id,
            'type': 'direct' if isinstance(sound, DirectSound) else 'echo',
            'status': sound.active
        }
        
        if isinstance(sound, EchoSound):
            data.update({
                'parent_id': sound.parent_id,
                'reflection_count': sound.reflection_count
            })
        
        return data
    
    def save_simulation_data(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a proper dictionary of constants
        constants_dict = {
            'ARENA_WIDTH': Constants.ARENA_WIDTH,
            'ARENA_HEIGHT': Constants.ARENA_HEIGHT,
            'SOUND_SPEED': Constants.SOUND_SPEED,
            'BAT_SPEED': Constants.BAT_SPEED,
            'SIM_DURATION': Constants.SIM_DURATION,
            'TIME_STEP': Constants.TIME_STEP,
            'CALL_DURATION': Constants.CALL_DURATION,
            'CALL_RATE': Constants.CALL_RATE,
            'OBSTACLE_COUNT': Constants.OBSTACLE_COUNT,
            'OBSTACLE_RADIUS': Constants.OBSTACLE_RADIUS,
            'EMITTED_SPL': Constants.EMITTED_SPL,
            'MIN_DETECTABLE_SPL': Constants.MIN_DETECTABLE_SPL,
            'NUM_BATS': Constants.NUM_BATS,
            'AIR_ABSORPTION': Constants.AIR_ABSORPTION,
            'REFLECTION_LOSS': Constants.REFLECTION_LOSS,
            'SOUND_RADIUS': Constants.SOUND_RADIUS,
            'MAX_REFLECTIONS': Constants.MAX_REFLECTIONS,
            'timestamp': timestamp
        }
        
        simulation_data = {
            'parameters': constants_dict,  # Use the plain dictionary
            'bat_data': [],
            'obstacle_positions': [(o.position.x, o.position.y) for o in self.obstacles],
            'sound_history': self.history
        }
        
        for bat in self.bats:
            bat_data = {
                'id': bat.id,
                'position_history': bat.position_history,
                'received_sounds': bat.received_sounds,
                'emitted_sounds': [{
                    'creation_time': s.creation_time,
                    'origin': (s.origin.x, s.origin.y),
                    'initial_spl': s.initial_spl
                } for s in bat.emitted_sounds]
            }
            simulation_data['bat_data'].append(bat_data)
        
        filename = f"bat_simulation_{timestamp}.pkl"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'wb') as f:
            pickle.dump(simulation_data, f)
        
        print(f"Saved simulation data to {filepath}")
    
    def visualize(self):
        def init():
            for marker in self.bat_markers:
                marker.set_data([], [])
            return self.bat_markers
        
        def animate(i):
            frame = self.history[i]
            
            for j, (x, y) in enumerate(frame['bat_positions']):
                self.bat_markers[j].set_data([x], [y])
            
            for artist in self.sound_artists + self.detection_artists:
                artist.remove()
            self.sound_artists.clear()
            self.detection_artists.clear()
            plt.title(f'time step: {i}')
            colors = plt.cm.tab10.colors
            for sound in frame['sound_objects']:
                # print(sound)
                if not sound['status']:
                    continue

                emitter_color = colors[sound['emitter_id'] % len(colors)]
                alpha = 0.5 - (0.1 * sound.get('reflection_count', 0))
                
                inner = max(0, sound['radius'] - Constants.SOUND_RADIUS)
                outer = sound['radius']

                if inner < outer :
                    if sound['type'] == 'direct':
                        linestyle = '-'
                        hatching_of_disk= '++'
                    else:
                        linestyle = '--'
                        alpha=0.5*alpha
                        hatching_of_disk= '..'
                    if inner==0:
                        width_of_disk = sound['radius']
                    else:
                        width_of_disk = Constants.SOUND_RADIUS
                    wedge = Wedge(sound['origin'], outer, 0, 360, 
                                width=width_of_disk,
                                fill=False, color=emitter_color,
                                alpha=alpha, linestyle=linestyle, hatch=hatching_of_disk)
                    self.ax.add_patch(wedge)
                    self.sound_artists.append(wedge)
            
            # for bat_idx, detections in enumerate(frame['bat_detections']):
            #     for detection in detections:
            #         if detection['type'] == 'direct':
            #             color = 'green'
            #         else:
            #             color = colors[detection['emitter_id'] % len(colors)]
                    
            #         dx, dy = detection['position']
            #         marker = Circle((dx, dy), 0.05, color=color, alpha=0.7)
            #         self.ax.add_patch(marker)
            #         self.detection_artists.append(marker)
                    
            #         bat_x, bat_y = frame['bat_positions'][bat_idx]
            #         line, = self.ax.plot([bat_x, dx], [bat_y, dy],
            #                            color=color, alpha=0.2)
            #         self.detection_artists.append(line)
            
            return self.bat_markers + self.sound_artists + self.detection_artists
        
        ani = animation.FuncAnimation(
            self.fig, animate, frames=len(self.history),
            init_func=init, blit=False, interval=Constants.FRAME_RATE
        )

        self.handles, labels = self.ax.get_legend_handles_labels()

        Obstacle_patch= Patch(color='red', alpha=0.5, label='Obstacle')
        DirectSound_patch = Patch(hatch="++", label='DirectSound')
        EchoSound_patch = Patch(hatch="..", label='EchoSound')

        self.handles.append(DirectSound_patch); self.handles.append(EchoSound_patch); self.handles.append(Obstacle_patch)
        # DirectSound_patch = Patch(hatch="++", label='DirectSound')
        # plt.legend()
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), handles=self.handles)

        # FFwriter = animation.FFMpegWriter(fps=30, extra_args=['-vcodec', 'libx264'])
        # ani.save(self.output_dir+f"/animation_numbats_{Constants.NUM_BATS}_numobs_{Constants.OBSTACLE_COUNT}_time_{Constants.SIM_DURATION}_call_duration_{Constants.CALL_DURATION}_call_rate_{Constants.CALL_RATE}_frame_rate_{Constants.FRAME_RATE}.gif")
        plt.show()

if __name__ == "__main__":
    sim = Simulation()
    sim.run()