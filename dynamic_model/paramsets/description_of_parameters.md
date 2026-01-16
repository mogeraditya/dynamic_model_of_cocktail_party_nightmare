# Description of the parameters

Parameters crucial for the simulation are described in this file. Details about the units are also provided. Search the repo for the specific parameter in order to find out how it is implemented. 
### 1. Parameters related to sound propagation:

1. "SOUND_SPEED": Speed of sound in S.I. units (m/s)
2. "AIR_ABSORPTION": Sound energy absorbed by the medium (dB/m). This is only place where sound frequency range of the bat calls matter within the scope of the model, all sounds are assumed to be of the same frequency of this given absorption. Change this based on the average sound frequency of the bat being modelled. 
3. "REFLECTION_LOSS": Target strength of objects in the simulation, unless otherwise specified (dB SPL). This corresponds to the loss in intensity of sound when it reflects off any object. 
4. "REFLECTION_LOSS_WALL":  Target strength of wall panels in the simulation, unless otherwise specified (dB SPL). This corresponds to the loss in intensity of sound when it reflects off wall panels. Refer to 3.3 for more details about wall panels. 
### 2. Parameters related to simulation time:
1. "SIM_DURATION": Duration for which the simulation needs to be run (s)
2. "TIME_STEP": Step size of each iteration over which computations happen (s). This is the minimum time resolution of the simulation.
3. "FRAME_RATE": Frame rate of the output video (fps)
### 3. Parameters related to the arena and plotting: 
1. "ARENA_WIDTH": Width of the rectangular arena in which bats fly. (m)
2. "ARENA_LENGTH": Length of the rectangular arena in which bats fly. (m)
3. "WALL_RESOLUTION": Resolution of the wall panels (m). Walls only generate echoes from discrete points, this parameter sets the gap between these "echo-generating" points. 
4. "CLEANUP_INTERVAL": Number of iterations after which the agents throw away information stored in local memory. This is done while ensuring that bat decisions aren't affected.
5. "CLEANUP_PLOT_DATA": Periodicity with which the simulation information is stored. This is done in order to ensure that RAM doesn't overload.
6. "OBSTACLE_COUNT": Number of random obstacles to place in the arena. 
7. "OBSTACLE_RADIUS": Radius of each random obstacle (m).
8. "SPECIAL_BOUNDARY_RULES": Yes if you want complex shapes of arena. *Work in progress.*
### Parameters related to bats: >:)
1. "NUM_BATS": Number of bats in the simulation. 
2. "BAT_SPEED": Speed of the bat (m/s).
3. "BAT_FAST_SPEED": Speed of the bat when it decides to fly faster (m/s).
4. "BAT_RADIUS": Radius of the bat (m).
5. "CALL_DURATION": Duration of the bat call (s). We model FM bats, and hence duration corresponds to the time duration of a **single** call sweep.
6. "CALL_RATE": Frequency of the bat calls (Hz). We model FM bats, and hence frequency corresponds to the rate of emission of sweeps.
7. "CALL_RATE_FAST": Frequency of the bat calls when it decides to call faster (Hz). We model FM bats, and hence frequency corresponds to the rate of emission of sweeps.
8. "EMITTED_SPL": The sound pressure level at which the bat emits the call. (@1 m re 20muPa)
9. "HEARING_SPL": Minimum sound pressure level of a sound required for a bat to detect a sound. (dB SPL) 
10. "PROPENSITY_TO_CHANGE_DIRECTION": Probability that the bat randomly changes its direction. This is only allowed to happen once a call. Usually turned off in the simulation, but is a useful control.
11. "NOISE_IN_CALL_RATE": Noise in call rate (ms). Bat calls are not uniform i.e. 10 Hz call rate does not correspond to 100ms interval between two calls because it is noisy. This parameter handles the noise in the call rate. Noise modelled as a uniform distribution between +/- the value of the parameter.
12. "CALL_DIRECTIONALITY": Directionality factor of the bat call. Bat call intensity falls off with angle, with the highest intensity in the front of the bat and lowest immediately behind it.  
13. "HEARING_DIRECTIONALITY": Directionality factor of the bat's hearing. The same sound is perceived differently based on the angle at which the bat listens to it, highest if it arrives immediately in front of the bat and lowest if it comes from behind.
14. "BAT_ROTATION_SPEED": Rotation speed of the bat (radians/s)
15. "HEARING_ANGLE_THRESHOLD": Angle of hearing range of the bat (degrees) Sounds outside +/- angle of hearing range from the front of the bat are not heard by the bat. 
16. "SPATIAL_REFERENCE_FRAME": Spatial reference frame w.r.t. which the agent stores information. At the moment there are two implementations of this, "allocentric" and "egocentric". In *egocentric*, information about detected sounds is stored w.r.t. bats direction when it initially heard the sound. In *allocentric*, the information is stored w.r.t. an arbitrary/ random direction which is fixed for the whole duration of the simulation. 
17. "BEHAVIOUR_RULE":  Controller of choice. There are two options at the moment, "avoid-loudest-sound" and "consistency".
18. "KILL_MOVEMENT": *Do you really want to kill an innocent bat (Bool)?!*  Kills the bat's movement thus making it stationary. There is great demand in the market to use dead bats as jammers. :(
### Parameters related to bat signal perception 
1. "IMPLEMENT_SNR": Yes to implement signal to noise ratio based paradigm of sound detection (Bool). Refer to *r"./dynamic_model/utilities/snr_implementation.py"* for more details.
2. "MINIMUM_SOUND_DETECTION_FRACTION": Minimum fraction of the focal sound profile that needs to be above the total masking profile in order to be considered as detected. Refer to *r"./dynamic_model/utilities/snr_implementation.py"* for more details.
### Parameters related to bat behaviour :0
1. "TIME_DELAY_FOR_DIRECTION_CHANGE": Time post call after which bat makes a movement decision (s). Information collected during this time is used to make the decision, depending on controller of choice. 
2. "INCLUDE_DIRECT_SOUNDS_IN_RESPONSE":  Yes to include direct sounds in response, else false (Bool). Bats might be capable of telling apart, from the spectral properties, direct sounds of other bats from echoes.
3. "TIME_DELAY_THRESHOLD_FOR_REPULSION":  The maximum delay after call emission a response inducing sound can have in order to elicit a repulsion response in bat (s).

### Parameters related to avoid-loudest-sound controller :<
1. "SPL_THRESHOLD_FOR_ATTRACTION": Minimum SPL of loudest sound needed to elicit a attractive maneuver (dB SPL).
2. "SPL_THRESHOLD_FOR_REPULSION":  Minimum SPL of loudest sound needed to elicit a repulsive maneuver (dB SPL).

### Parameters related to consistency controller :>
1. "BAT_RADIAL_RESOLUTION": Minimum time difference between two sounds needed for the bat to perceive them as two different sounds (s). 
2. "BAT_ANGULAR_RESOLUTION": Minimum angular separation between two sounds needed for the bat to perceive them as two different sounds (degrees).
3. "MEMORY_WINDOW_FOR_CONSISTENCY": Number of calls over which movement decision is integrated over. Think of this as a moving window, i.e., if the value of this parameter was x, decision after the i-th call occurs after integrating information obtained from (i-x)-th call to i-th call. 
4. "CONVERT_GRIDS+TO_ONE_HOT_?": Yes if you want sound information to be converted to one hot encoding every call, no if you want to normalize based on the total number of sounds (Bool). 
5. "NUMBER_OF_CONSISTENT_IPIS_FOR_MOVEMENT":  Minimum number of calls over which information needs to be heard in order to be considered for response. 