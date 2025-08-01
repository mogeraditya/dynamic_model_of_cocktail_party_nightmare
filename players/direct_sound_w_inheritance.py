from supporting_files.vectors import Vector
import supporting_files.constants as Constants
import math
from players.echo_sound import EchoSound

class DirectSound(EchoSound):
    def __init__(self, origin, creation_time, emitter_id):
        super().__init__(origin=origin, creation_time=creation_time, emitter_id=emitter_id, initial_spl=Constants.EMITTED_SPL, parent_creation_time= Constants.EMITTED_SPL, reflection_count=0)

        # self.initial_spl = Constants.EMITTED_SPL
        self.current_spl = self.initial_spl
        self.current_radius = 0
        self.max_radius = Constants.SOUND_DISK_WIDTH # Keep track of vada size
        self.active = True
        self.has_reflected = False  # Direct sounds can only reflect once/ i.e. per collision only one echo ngl
        self.reflected_obstacles = set() # Track obstacles that iit reflected off of in order to cap this in the future
        
    
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
    

