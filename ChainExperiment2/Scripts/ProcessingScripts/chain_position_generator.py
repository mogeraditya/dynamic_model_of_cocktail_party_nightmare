import numpy as np

# parameters from paper; Tuninetti et al 2021.
CHAIN_SPACING = 0.2  # in meters
CHAIN_RADIUS = 0.1  # in meters
NUMBER_OF_CHAINS_IN_BOUNDARIES = 5

# parameters we want to vary
CORRIDOR_WIDTH = 0.4  # in mters


def find_chain_positions(corridor_width):
    corridor_width = CORRIDOR_WIDTH

    # we want to make a cross like chamber; refer to hand drawn diagram in the report :p

    # base chains; chains that dont change with turn direction
    base_chains_x = []
    base_chains_y = []
    # first make a unit square of chains, then copy paste them as required.

    chain_unit_box_x = np.arange(
        CHAIN_SPACING,
        CHAIN_SPACING * NUMBER_OF_CHAINS_IN_BOUNDARIES + CHAIN_SPACING,
        CHAIN_SPACING,
    )
    np.concat((chain_unit_box_x, chain_unit_box_x
        + corridor_width
        + CHAIN_SPACING * NUMBER_OF_CHAINS_IN_BOUNDARIES))
    chain_unit_box_y = chain_unit_box_x.copy()
    chain_unit_box_y.extend(chain_unit_box_y + CHAIN_SPACING * NUMBER_OF_CHAINS_IN_BOUNDARIES)

   

    # now make special case for left turn right turn and straight
    # what needs to be added 
    straight_missing_box_x = base_chains_x.copy()
    straight_missing_box_y = np.arange(CHAIN_SPACING + 2* CHAIN_SPACING * NUMBER_OF_CHAINS_IN_BOUNDARIES, CHAIN_SPACING + 2* CHAIN_SPACING * NUMBER_OF_CHAINS_IN_BOUNDARIES +corridor_width, CHAIN_SPACING)
    
    left_missing_box_x = 