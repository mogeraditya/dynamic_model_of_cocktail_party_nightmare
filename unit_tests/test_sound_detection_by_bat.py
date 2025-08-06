import sys
sys.path.insert(1, '.')
from supporting_files.vectors import Vector
import math
from players.direct_sound_w_inheritance import DirectSound
from players.echo_sound import EchoSound
from players.bat import Bat
import random
from supporting_files.misc_files import *
        
parameters_dict= load_parameters('\paramsets\mycsvfiles.csv')
position= Vector(
            random.uniform(1, parameters_dict["ARENA_WIDTH"] - 1),
            random.uniform(1, parameters_dict["ARENA_HEIGHT"] - 1)
        )
sound = DirectSound(
                origin=position,
                creation_time=0,
                emitter_id=0
            )
print(isinstance(sound, EchoSound))
