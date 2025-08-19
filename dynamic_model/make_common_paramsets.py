"""Save common simulation parameters;
This will be used as a template for other parameters to build upon"""

import pandas as pd

simulation_parameters = pd.DataFrame()

simulation_parameters["SIM_DURATION"] = [10]  # s; duration of the simulation
# simulation_parameters["FRAME_RATE"] = 100 # frame rate of the
simulation_parameters["CLEANUP_INTERVAL"] = (
    0.1  # s; seconds after which memory of bat is cleared
)
simulation_parameters["CLEANUP_PLOT_DATA"] = (
    1000  # iterations; number of iterations of simulation after which data is stored for plotting
)
simulation_parameters["ARENA_WIDTH"] = 7  # m; width of arena
simulation_parameters["ARENA_HEIGHT"] = 5  # m; height of arena
simulation_parameters["TIME_STEP"] = 0.001  # s; time step of simulation

simulation_parameters["SOUND_SPEED"] = 343  # m/s; speed of sound
simulation_parameters["AIR_ABSORPTION"] = 1  # absorption of medium
simulation_parameters["REFLECTION_LOSS"] = 0.5  # dB loss per reflection


simulation_parameters["BAT_SPEED"] = 10  # m/s; speed of bat
simulation_parameters["BAT_RADIUS"] = 0  # m; radius of bat
simulation_parameters["EMITTED_SPL"] = 140  # dB; emitted spl of bat call
simulation_parameters["MIN_DETECTABLE_SPL"] = (
    20  # dB; spl level below whih a bat cannot detect a sound
)
simulation_parameters["NUM_BATS"] = 1  # number of bats in the simulation
simulation_parameters["CALL_DURATION"] = 0.005  # s; duration of each call
simulation_parameters["CALL_RATE"] = 10  # Hz; frequency of bat calls
simulation_parameters["PROPENSITY_TO_CHANGE_DIRECTION"] = (
    0.001  # probability of changing direction, used for random walk of bat
)

simulation_parameters["OBSTACLE_COUNT"] = 0  # number of obstacles
simulation_parameters["OBSTACLE_RADIUS"] = 0.1  # m; radius of obstacles


DIR_TO_SAVE_COMMON_PARAMETERS = "./dynamic_model/common_parameters.csv"
simulation_parameters.to_csv(DIR_TO_SAVE_COMMON_PARAMETERS)
print(simulation_parameters)
