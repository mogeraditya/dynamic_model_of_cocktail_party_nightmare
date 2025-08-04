import sys
sys.path.insert(1, '.')
# from __future__ import absolute_import
# sys.path.append('..//')
# # import simulation 
import os
# os.chdir("..//")
origin=0; current_radius=0.3
print(f'DirectSound(origin={origin}, radius={current_radius:.2f}, ')
print(os.getcwd())
from supporting_files.vectors import Vector
import supporting_files.constants as Constants
import math
from players.direct_sound_w_inheritance import DirectSound
from players.echo_sound import EchoSound

import random        
position= Vector(
            random.uniform(1, self.parameters_dict["ARENA_WIDTH"] - 1),
            random.uniform(1, self.parameters_dict["ARENA_HEIGHT"] - 1)
        )
sound = DirectSound(
                origin=position,
                creation_time=0,
                emitter_id=0
            )
print(isinstance(sound, EchoSound))

