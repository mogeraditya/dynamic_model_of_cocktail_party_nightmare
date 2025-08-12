from supporting_files.vectors import Vector
import supporting_files.constants as Constants
import math
from agents.echo_sound import EchoSound

class DirectSound:
    def __init__(self, origin, creation_time, emitter_id):
        self.origin = origin
        self.creation_time = creation_time
        self.emitter_id = emitter_id
        self.initial_spl = Constants.EMITTED_SPL
        self.current_spl = self.initial_spl
        self.current_radius = 0.01
        self.max_radius = Constants.SOUND_SPEED * Constants.CALL_DURATION # Keep track of vada size
        self.active = True
        self.has_reflected = False  # Direct sounds can only reflect once/ i.e. per collision only one echo ngl
        self.reflected_obstacles = set() # Track obstacles that iit reflected off of in order to cap this in the future
        
    def update(self, current_time):
        elapsed = current_time - self.creation_time 
        self.current_radius = Constants.SOUND_SPEED * elapsed
        
        # Calculate SPL with distance and air absorption

        if self.current_radius > 0:
            distance_effect = 20 * math.log10(self.current_radius/0.1)
            # print(distance_effect); print((Constants.AIR_ABSORPTION * self.current_radius)); print(self.initial_spl)
            self.current_spl = self.initial_spl - distance_effect - (Constants.AIR_ABSORPTION * self.current_radius)
        
        # if current_time >= self.creation_time + Constants.CALL_DURATION:
        #     self.active = False
        
        if self.check_if_sound_outside_arena_simpler():
            self.active = False
    
    def contains_point(self, point):
        """Check if point is within the sound disk"""
        distance = self.origin.distance_to(point)
        return distance <= self.current_radius and distance >= max(0, self.current_radius - Constants.SOUND_DISK_WIDTH)
    
    def create_echo(self, point, current_time, normal):
        if self.has_reflected:
            return None
            
        reflected_spl = self.current_spl - Constants.REFLECTION_LOSS
        if reflected_spl < Constants.MIN_DETECTABLE_SPL:
            return None
        
        # self.has_reflected = True
        echo = EchoSound(
            origin=point,
            creation_time=current_time,
            emitter_id=self.emitter_id,
            initial_spl=reflected_spl,
            parent_creation_time=self.creation_time,
            reflection_count=1
        )
        echo.reflected_obstacles.update(self.reflected_obstacles)
        return echo
    
    def __repr__(self):
        return (f"DirectSound(origin={self.origin}, radius={self.current_radius:.2f}, "
                f"spl={self.current_spl:.1f}dB, emitter={self.emitter_id})")
    
    # TODO : fix the function that checks if sound is out of the arena in order to kill it later
    def check_if_sound_outside_arena(self):
        points_the_define_arena= [Vector(0.0,0.0), Vector(0.0, self.parameters_df["ARENA_HEIGHT"][0]), Vector(self.parameters_df["ARENA_WIDTH"][0], 0.0), Vector(self.parameters_df["ARENA_WIDTH"][0], self.parameters_df["ARENA_HEIGHT"][0])]
        counter= 0
        for point in points_the_define_arena:
            distance = self.origin.distance_to(point)
            if distance <= self.current_radius:
                counter+=1
        if counter==4:
            return False
        
    def check_if_sound_outside_arena_simpler(self):
        if (self.current_radius)>max(self.parameters_df["ARENA_HEIGHT"][0], self.parameters_df["ARENA_WIDTH"][0]):
            return True
        else:
            return False