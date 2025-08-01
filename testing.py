from supporting_files.vectors import Vector
import supporting_files.constants as Constants
import math
from players.direct_sound_w_inheritance import DirectSound
from players.echo_sound import EchoSound

import random        
position= Vector(
            random.uniform(1, Constants.ARENA_WIDTH - 1),
            random.uniform(1, Constants.ARENA_HEIGHT - 1)
        )
sound = DirectSound(
                origin=position,
                creation_time=0,
                emitter_id=0
            )
print(isinstance(sound, EchoSound))